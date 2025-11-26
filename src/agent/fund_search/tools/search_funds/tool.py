import json
import os

import dspy
import duckdb

from src.agent.fund_search.models.query import FundSearchCriteria
from src.agent.fund_search.utils.mappings import EntityMapper


class FundSearchTool(dspy.Module):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        # Load entity correlations
        self.entity_map = {}
        map_path = "src/infrastructure/database/extracted/entity_correlations.json"
        if os.path.exists(map_path):
            try:
                with open(map_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self.entity_map = data.get("groups", {})
            except Exception as e:
                print(f"Warning: Failed to load entity map in FundSearchTool: {e}")

    def forward(
        self,
        criteria: FundSearchCriteria,
        name: str | None = None,
        cnpjs: list[str] | None = None,
        limit: int = 50,
    ) -> list[str]:
        """Search funds by metadata criteria. Returns list of CNPJs."""
        try:
            conn = duckdb.connect(self.db_path, read_only=True)
            conditions = ["status != 'CANCELLED'"]

            # 1. Entity Search Logic (Service Provider Matching)
            entity_cnpjs = []
            if criteria.service_provider_entity:
                # Handle list of entities
                entities = criteria.service_provider_entity

                for entity_name in entities:
                    # Normalize entity name
                    normalized_key = EntityMapper.normalize_provider(entity_name)
                    if normalized_key and normalized_key in self.entity_map:
                        entity_data = self.entity_map[normalized_key]
                        # Collect all CNPJs for this entity across all roles
                        for role in ["MANAGER"]:
                            if role in entity_data:
                                for ent in entity_data[role]:
                                    if "tax_id" in ent:
                                        entity_cnpjs.append(ent["tax_id"])

            # 2. Name Search Logic
            name_clause = ""
            if name:
                # Lowercase search for case-insensitive matching
                name_clause = f"(LOWER(legal_name) LIKE LOWER('%{name}%'))"

            # 3. Combine Name and Entity Logic
            if entity_cnpjs and name_clause:
                cnpj_list_str = "', '".join(entity_cnpjs)
                # Ensure we only match if they are the MANAGER
                provider_clause = f"len(list_filter(service_providers, x -> x.tax_id IN ('{cnpj_list_str}') AND x.type = 'MANAGER')) > 0"
                conditions.append(f"({name_clause} AND {provider_clause})")

            elif entity_cnpjs:
                cnpj_list_str = "', '".join(entity_cnpjs)
                conditions.append(
                    f"len(list_filter(service_providers, x -> x.tax_id IN ('{cnpj_list_str}') AND x.type = 'MANAGER')) > 0"
                )

            # Fallback: If searching by service provider but no entity map match found
            # Use the provided name as a text search against manager names or legal name
            elif criteria.service_provider_entity and not entity_cnpjs:
                # We interpret this as: User wants funds managed by "NAME", but we couldn't resolve "NAME" to a CNPJ.
                # So we search for "NAME" inside the service_providers JSON string (specifically matching manager pattern if possible,
                # but simple text search is safer for robustness).

                # Construct OR clauses for each unmapped entity
                fallback_clauses = []
                for entity_name in criteria.service_provider_entity:
                    # Clean the name for safe SQL insertion
                    safe_name = entity_name.replace("'", "''")

                    # Search in service_providers (as manager) OR in fund legal_name
                    # Note: searching raw JSON string is a bit hacky but works for text match
                    fallback_clauses.append(f"""(
                        CAST(service_providers AS VARCHAR) ILIKE '%{safe_name}%' 
                        OR legal_name ILIKE '%{safe_name}%'
                    )""")

                if fallback_clauses:
                    fallback_condition = " OR ".join(fallback_clauses)
                    if name_clause:
                        conditions.append(f"({name_clause} AND ({fallback_condition}))")
                    else:
                        conditions.append(f"({fallback_condition})")

            elif name_clause:
                conditions.append(f"""(
                        {name_clause}
                        OR CAST(service_providers AS VARCHAR) ILIKE '%{name}%'
                    )""")

            if criteria.fund_type:
                types_str = "', '".join(criteria.fund_type)
                conditions.append(f"fund_type IN ('{types_str}')")

            if criteria.investment_class:
                classes_str = "', '".join(criteria.investment_class)
                conditions.append(f"investment_class IN ('{classes_str}')")

            if criteria.target_audience:
                audiences_str = "', '".join(criteria.target_audience)
                conditions.append(f"target_audience IN ('{audiences_str}')")

            # Boolean/Extra criteria
            if criteria.fund_of_funds is not None:
                conditions.append(f"is_fund_of_funds = {str(criteria.fund_of_funds).upper()}")

            if criteria.is_exclusive_fund is not None:
                conditions.append(f"is_exclusive_fund = {str(criteria.is_exclusive_fund).upper()}")

            if criteria.can_invest_abroad_100_pct is not None:
                conditions.append(
                    f"can_invest_abroad_100_pct = {str(criteria.can_invest_abroad_100_pct).upper()}"
                )

            if criteria.has_long_term_taxation is not None:
                conditions.append(
                    f"has_long_term_taxation = {str(criteria.has_long_term_taxation).upper()}"
                )

            if criteria.manager_type:
                managers_str = "', '".join(criteria.manager_type)
                conditions.append(f"manager_type IN ('{managers_str}')")

            if cnpjs:
                cnpjs_str = "', '".join(cnpjs)
                # Filter by CNPJ
                conditions.append(
                    f"list_filter(identifiers, x -> x.type = 'CNPJ')[1].value IN ('{cnpjs_str}')"
                )

            where_clause = " AND ".join(conditions)

            # Default sort by Net Asset Value (AUM) to return most relevant funds first
            # We only select CNPJ
            query = f"""
                SELECT 
                    list_filter(identifiers, x -> x.type = 'CNPJ')[1].value as cnpj
                FROM funds
                WHERE {where_clause}
                ORDER BY net_asset_value.value DESC
                LIMIT {limit}
                """

            rows = conn.execute(query).fetchall()
            conn.close()

            # Return list of CNPJs
            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error in search_funds: {e}")
            return []
