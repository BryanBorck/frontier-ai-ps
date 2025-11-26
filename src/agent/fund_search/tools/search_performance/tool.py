from datetime import datetime, timedelta

import dspy
import duckdb

from src.agent.fund_search.models.query import NumericFilter


class PerformanceSearchTool(dspy.Module):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def forward(
        self,
        numeric_filter: NumericFilter,
        cnpjs: list[str] | None = None,
        limit: int = 20,
    ) -> list[str]:
        """Search funds based on performance criteria (returns vs benchmark). Returns list of CNPJs."""
        if numeric_filter.metric != "return":
            return []

        # Determine benchmark value
        benchmark_val = 0.0
        if numeric_filter.benchmark_name == "CDI":
            benchmark_val = 10.0
        elif numeric_filter.benchmark_name == "SELIC":
            benchmark_val = 10.5
        elif numeric_filter.value:
            benchmark_val = numeric_filter.value

        operator = (
            ">"
            if numeric_filter.operator == "min"
            else "<"
            if numeric_filter.operator == "max"
            else ">"
        )

        # Dynamic Date Filtering
        today = datetime.now()
        cutoff_date = today - timedelta(days=365)

        if numeric_filter.performance_period:
            if numeric_filter.performance_period == "ytd":
                cutoff_date = datetime(today.year, 1, 1)
            else:
                try:
                    m = int(numeric_filter.performance_period.replace("m", ""))
                    cutoff_date = today - timedelta(days=m * 30)
                except ValueError:
                    pass

        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        try:
            conn = duckdb.connect(self.db_path, read_only=True)

            cnpj_filter = ""
            if cnpjs:
                cnpjs_str = "', '".join(cnpjs)
                # Filter in the outer query after join
                cnpj_filter = f"AND list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value IN ('{cnpjs_str}')"

            query = f"""
                WITH recent_perf AS (
                    SELECT
                        fund_id,
                        fund_id.value as id_val,
                        SUM(return_pct) as total_return
                    FROM fund_performance_indicators
                    WHERE first_date >= '{cutoff_str}'
                    GROUP BY fund_id, fund_id.value
                    HAVING total_return {operator} {benchmark_val}
                )
                SELECT
                    list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value as cnpj
                FROM recent_perf rp
                JOIN funds f ON rp.fund_id = f.fund_id
                WHERE 1=1 {cnpj_filter}
                ORDER BY rp.total_return DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error in search_performance: {e}")
            return []
