import dspy
import duckdb

from src.agent.fund_search.models.query import PositionSearchCriteria


class PositionSearchTool(dspy.Module):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def forward(
        self,
        criteria: PositionSearchCriteria,
        cnpjs: list[str] | None = None,
        limit: int = 50,
    ) -> list[str]:
        """Search funds by their asset positions/holdings. Returns list of CNPJs."""
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

            if cnpjs:
                cnpjs_str = "', '".join(cnpjs)
                conditions.append(f"cnpj IN ('{cnpjs_str}')")

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Aggregate exposure per fund
            query = f"""
                SELECT
                    cnpj,
                    SUM(position_value) as total_exposure
                FROM fund_positions
                WHERE {where_clause}
                GROUP BY cnpj
                ORDER BY total_exposure DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            # row[0] is CNPJ
            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error in search_positions: {e}")
            return []
