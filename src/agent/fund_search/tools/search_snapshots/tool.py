import dspy
import duckdb

from src.agent.fund_search.models.query import NumericFilter


class SnapshotSearchTool(dspy.Module):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def forward(
        self,
        numeric_filter: NumericFilter,
        cnpjs: list[str] | None = None,
        limit: int = 50,
    ) -> list[str]:
        """Search funds by latest snapshot metrics (AUM, Holders). Returns list of CNPJs."""
        try:
            conn = duckdb.connect(self.db_path, read_only=True)

            metric_col = "net_assets_value" if numeric_filter.metric == "aum" else "number_of_holders"

            operator_map = {"min": ">=", "max": "<=", "top": ">="}
            operator = operator_map.get(numeric_filter.operator, ">=")

            value_threshold = numeric_filter.value if numeric_filter.value else 0

            fund_filter = ""
            if cnpjs:
                cnpjs_str = "', '".join(cnpjs)
                fund_filter = f"AND cnpj IN ('{cnpjs_str}')"

            query = f"""
                SELECT
                    cnpj
                FROM fund_snapshots
                WHERE {metric_col}.value {operator} {value_threshold}
                {fund_filter}
                ORDER BY {metric_col}.value DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error in search_snapshots: {e}")
            return []
