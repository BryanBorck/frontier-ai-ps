import json
import os

import dspy
import duckdb

from src.agent.models.fund import FundResult
from src.agent.models.query import FundSearchCriteria
from src.agent.utils.mappings import EntityMapper


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
        fund_ids: list[str] | None = None,
        limit: int = 50,
    ) -> list[FundResult]:
        """Search funds by metadata criteria."""
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
                        for role in ["MANAGER", "ADMINISTRATOR", "CUSTODIAN"]:
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
                provider_clause = (
                    f"len(list_filter(service_providers, x -> x.tax_id IN ('{cnpj_list_str}'))) > 0"
                )
                conditions.append(f"({name_clause} AND {provider_clause})")

            elif entity_cnpjs:
                cnpj_list_str = "', '".join(entity_cnpjs)
                conditions.append(
                    f"len(list_filter(service_providers, x -> x.tax_id IN ('{cnpj_list_str}'))) > 0"
                )

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

            if fund_ids:
                ids_str = "', '".join(fund_ids)
                conditions.append(f"fund_id.value IN ('{ids_str}')")

            where_clause = " AND ".join(conditions)

            # Default sort by Net Asset Value (AUM) to return most relevant funds first
            query = f"""
                SELECT 
                    fund_id.value as fund_id,
                    list_filter(identifiers, x -> x.type = 'CNPJ')[1].value as cnpj,
                    legal_name,
                    fund_type,
                    investment_class,
                    target_audience,
                    net_asset_value.value as aum
                FROM funds
                WHERE {where_clause}
                ORDER BY net_asset_value.value DESC
                LIMIT {limit}
                """

            rows = conn.execute(query).fetchall()
            conn.close()

            results = [
                FundResult(
                    fund_id=row[0],
                    cnpj=row[1] or "",
                    legal_name=row[2],
                    fund_type=row[3],
                    investment_class=row[4],
                    target_audience=row[5],
                    aum=row[6],
                )
                for row in rows
            ]
            return results
        except Exception as e:
            print(f"Error in search_funds: {e}")
            return []
