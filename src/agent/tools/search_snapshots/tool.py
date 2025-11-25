import dspy
import duckdb

from src.agent.models.fund import FundResult
from src.agent.models.query import NumericFilter


class SnapshotSearchTool(dspy.Module):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def forward(
        self,
        numeric_filter: NumericFilter,
        fund_ids: list[str] | None = None,
        limit: int = 50,
    ) -> list[FundResult]:
        """Search funds by latest snapshot metrics (AUM, Holders)."""
        try:
            conn = duckdb.connect(self.db_path, read_only=True)

            metric_col = "net_assets_value" if numeric_filter.metric == "aum" else "number_of_holders"

            operator_map = {"min": ">=", "max": "<=", "top": ">="}
            operator = operator_map.get(numeric_filter.operator, ">=")

            value_threshold = numeric_filter.value if numeric_filter.value else 0

            fund_filter = ""
            if fund_ids:
                ids_str = "', '".join(fund_ids)
                fund_filter = f"AND fund_id.value IN ('{ids_str}')"

            query = f"""
                SELECT
                    fund_id.value as fund_id,
                    cnpj,
                    fund_name,
                    net_assets_value,
                    number_of_holders
                FROM fund_snapshots
                WHERE {metric_col} {operator} {value_threshold}
                {fund_filter}
                ORDER BY {metric_col} DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            results = [
                FundResult(
                    fund_id=row[0],
                    cnpj=row[1] or "",
                    legal_name=row[2],
                    aum=row[3],
                    holders=row[4],
                )
                for row in rows
            ]
            return results
        except Exception as e:
            print(f"Error in search_snapshots: {e}")
            return []
