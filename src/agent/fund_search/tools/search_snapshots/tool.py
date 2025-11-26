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

            # Map metric to column name and build metric expression
            # Note: net_assets_value is a STRUCT with .value, number_of_holders is a DOUBLE
            if numeric_filter.metric == "aum":
                metric_col = "s.net_assets_value.value"
                order_col = "s.net_assets_value.value"
            else:  # holders
                metric_col = "s.number_of_holders"
                order_col = "s.number_of_holders"

            # Map operator to SQL operator
            operator_map = {"min": ">=", "max": "<=", "top": ">="}
            operator = operator_map.get(numeric_filter.operator, ">=")

            value_threshold = numeric_filter.value if numeric_filter.value else 0

            # Build CNPJ filter
            fund_filter = ""
            if cnpjs:
                cnpjs_str = "', '".join(cnpjs)
                fund_filter = f"AND list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value IN ('{cnpjs_str}')"

            # Query with JOIN to get CNPJ from funds table
            # Use latest snapshot for each fund
            query = f"""
                WITH latest_snapshots AS (
                    SELECT
                        fund_id,
                        net_assets_value,
                        number_of_holders,
                        timestamp,
                        ROW_NUMBER() OVER (PARTITION BY fund_id ORDER BY timestamp DESC) as rn
                    FROM fund_snapshots
                )
                SELECT DISTINCT
                    list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value as cnpj
                FROM latest_snapshots s
                JOIN funds f ON s.fund_id = f.fund_id
                WHERE s.rn = 1
                  AND {metric_col} {operator} {value_threshold}
                  {fund_filter}
                ORDER BY {order_col} DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error in search_snapshots: {e}")
            return []
