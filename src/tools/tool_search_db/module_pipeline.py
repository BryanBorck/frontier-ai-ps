"""Database search module for Brazilian investment funds."""

import json
import os

import duckdb
from pydantic import BaseModel, Field

from src.tools.tool_parse_query.module_pipeline import FundSearchCriteria

# Load entity correlations
ENTITY_MAP_PATH = "src/infrastructure/database/extracted/entity_correlations.json"
ENTITY_MAP = {}

if os.path.exists(ENTITY_MAP_PATH):
    try:
        with open(ENTITY_MAP_PATH, encoding="utf-8") as f:
            data = json.load(f)
            ENTITY_MAP = data.get("groups", {})
    except Exception as e:
        print(f"Warning: Failed to load entity map: {e}")


class FundResult(BaseModel):
    """Result model for a single fund."""

    legal_name: str = Field(..., description="Legal name of the fund")
    cnpj: str = Field(..., description="CNPJ identifier")
    fund_type: str | None = Field(None, description="Fund type (FI, FIP, FIDC, etc.)")
    investment_class: str | None = Field(
        None, description="Investment class (Multimercado, Ações, etc.)"
    )


def search_funds(
    criteria: FundSearchCriteria,
    db_path: str = "src/infrastructure/database/br_funds.db",
    limit: int = 10,
) -> list[FundResult]:
    """Search for funds in the database using structured criteria.

    Args:
        criteria: Structured search criteria
        db_path: Path to the DuckDB database
        limit: Maximum number of results to return

    Returns:
        List of FundResult objects with fund metadata
    """
    conn = duckdb.connect(db_path, read_only=True)

    # Build the WHERE clause
    where_clauses = []
    params = {}

    # Entity Search Logic (Service Provider Matching)
    # This logic matches funds where ANY of the service providers (Manager, Admin, Custodian)
    # match the known CNPJs for the requested entity.
    entity_cnpjs = []

    if criteria.service_provider_entity and criteria.service_provider_entity in ENTITY_MAP:
        entity_data = ENTITY_MAP[criteria.service_provider_entity]

        # Collect all CNPJs for this entity across all roles
        for role in ["MANAGER", "ADMINISTRATOR", "CUSTODIAN"]:
            if role in entity_data:
                for entity in entity_data[role]:
                    if "tax_id" in entity:
                        entity_cnpjs.append(entity["tax_id"])

    # Text Search Logic (Fund Name)
    name_clause = ""
    if criteria.fund_legal_name:
        name_clause = "LOWER(legal_name) LIKE LOWER('%' || $legal_name || '%')"
        params["legal_name"] = criteria.fund_legal_name

    # Combine Entity and Name Logic
    # If we have BOTH entity CNPJs and a name, we want funds that match EITHER:
    # 1. The name text pattern (classic search)
    # 2. OR contain one of the entity's service providers
    # This ensures we don't miss funds that don't have the bank name in the title.

    if entity_cnpjs and name_clause:
        # We have both: (Name matches OR Provider matches)
        # However, checking hundreds of CNPJs in a list might be slow in SQL string construction
        # Optimization: Use list_contains or similar if possible, but DuckDB 'IN' is fine for <100 items

        # Use param based IN clause
        # Note: DuckDB Python client list binding can be tricky, so we join strings safely here since they are tax_ids
        cnpj_list_str = "', '".join(entity_cnpjs)

        # Build list of tax_id values from service_providers
        provider_clause = f"""
            len(list_filter(service_providers, x -> x.tax_id IN ('{cnpj_list_str}'))) > 0
        """

        where_clauses.append(f"({name_clause} OR {provider_clause})")

    elif entity_cnpjs:
        # Only entity search
        cnpj_list_str = "', '".join(entity_cnpjs)
        where_clauses.append(f"""
            len(list_filter(service_providers, x -> x.tax_id IN ('{cnpj_list_str}'))) > 0
        """)

    elif name_clause:
        # Only text search
        where_clauses.append(name_clause)

    if criteria.fund_type:
        where_clauses.append("fund_type = $fund_type")
        params["fund_type"] = criteria.fund_type

    if criteria.investment_class:
        where_clauses.append("investment_class = $investment_class")
        params["investment_class"] = criteria.investment_class

    if criteria.fund_of_funds is not None:
        where_clauses.append("is_fund_of_funds = $fund_of_funds")
        params["fund_of_funds"] = criteria.fund_of_funds

    if criteria.target_audience is not None:
        where_clauses.append("target_audience = $target_audience")
        params["target_audience"] = criteria.target_audience.value

    if criteria.manager_type is not None:
        where_clauses.append("manager_type = $manager_type")
        params["manager_type"] = criteria.manager_type.value

    if criteria.is_exclusive_fund is not None:
        where_clauses.append("is_exclusive_fund = $is_exclusive_fund")
        params["is_exclusive_fund"] = criteria.is_exclusive_fund

    if criteria.can_invest_abroad_100_pct is not None:
        where_clauses.append("can_invest_abroad_100_pct = $can_invest_abroad_100_pct")
        params["can_invest_abroad_100_pct"] = criteria.can_invest_abroad_100_pct

    if criteria.has_long_term_taxation is not None:
        where_clauses.append("has_long_term_taxation = $has_long_term_taxation")
        params["has_long_term_taxation"] = criteria.has_long_term_taxation

    # Always filter out cancelled funds
    where_clauses.append("status != 'CANCELLED'")

    # Build the query
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = f"""
        SELECT
            legal_name,
            list_filter(identifiers, x -> x.type = 'CNPJ')[1].value as cnpj,
            fund_type,
            investment_class
        FROM funds
        WHERE {where_sql}
        LIMIT {limit}
    """

    # Execute query
    try:
        result = conn.execute(query, params).fetchall()
    except Exception as e:
        print(f"Error executing query: {e}")
        # Fallback if service provider logic fails or something else goes wrong
        # Simplified query without provider logic if it was the cause
        if "list_filter(service_providers" in query:
            fallback_where = [c for c in where_clauses if "list_filter(service_providers" not in c]
            where_sql = " AND ".join(fallback_where) if fallback_where else "1=1"
            query = f"""
                SELECT
                    legal_name,
                    list_filter(identifiers, x -> x.type = 'CNPJ')[1].value as cnpj,
                    fund_type,
                    investment_class
                FROM funds
                WHERE {where_sql}
                LIMIT {limit}
            """
            result = conn.execute(query, params).fetchall()
        else:
            result = []

    conn.close()

    # Format results as FundResult objects
    funds = []
    for row in result:
        funds.append(
            FundResult(
                legal_name=row[0],
                cnpj=row[1],
                fund_type=row[2],
                investment_class=row[3],
            )
        )

    return funds


def execute(criteria: dict, limit: int = 10) -> list[dict]:
    """Execute the fund search tool.

    Args:
        criteria: Dictionary with search criteria
        limit: Maximum number of results to return

    Returns:
        List of dictionaries with fund metadata
    """
    # Convert dict to FundSearchCriteria
    search_criteria = FundSearchCriteria(**criteria)

    # Search for funds
    funds = search_funds(search_criteria, limit=limit)

    # Convert to list of dicts
    return [fund.model_dump() for fund in funds]
