import dspy
import duckdb

from src.agent.models.fund import FundResult
from src.agent.models.query import PositionSearchCriteria


class PositionSearchTool(dspy.Module):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def forward(
        self,
        criteria: PositionSearchCriteria,
        fund_ids: list[str] | None = None,
        limit: int = 50,
    ) -> list[FundResult]:
        """Search funds by their asset positions/holdings."""
        try:
            conn = duckdb.connect(self.db_path, read_only=True)
            conditions = []

            if criteria.asset_name:
                names_str = "', '".join(criteria.asset_name)
                conditions.append(f"asset_name IN ('{names_str}')")

            if criteria.asset_tickers:
                tickers_str = "', '".join(criteria.asset_tickers)
                conditions.append(f"ticker IN ('{tickers_str}')")

            if criteria.asset_type:
                types_str = "', '".join(criteria.asset_type)
                conditions.append(f"asset_type IN ('{types_str}')")

            if fund_ids:
                ids_str = "', '".join(fund_ids)
                conditions.append(f"fund_id.value IN ('{ids_str}')")

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            query = f"""
                SELECT
                    fund_id.value as fund_id,
                    cnpj,
                    fund_name,
                    asset_name,
                    position_value
                FROM fund_positions
                WHERE {where_clause}
                ORDER BY position_value DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            results = [
                FundResult(
                    fund_id=row[0],
                    cnpj=row[1] or "",
                    legal_name=row[2],
                    asset_name=row[3],
                    position_value=row[4],
                )
                for row in rows
            ]
            return results
        except Exception as e:
            print(f"Error in search_positions: {e}")
            return []
