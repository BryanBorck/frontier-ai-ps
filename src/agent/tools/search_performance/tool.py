from datetime import datetime, timedelta

import dspy
import duckdb

from src.agent.models.fund import FundResult
from src.agent.models.query import NumericFilter


class PerformanceSearchTool(dspy.Module):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def forward(
        self,
        numeric_filter: NumericFilter,
        limit: int = 20,
    ) -> list[FundResult]:
        """Search funds based on performance criteria (returns vs benchmark)."""
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
                    f.legal_name,
                    list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value as cnpj,
                    f.fund_type,
                    f.investment_class,
                    rp.total_return,
                    rp.id_val
                FROM recent_perf rp
                JOIN funds f ON rp.fund_id = f.fund_id
                ORDER BY rp.total_return DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            results = [
                FundResult(
                    fund_id=r[5],
                    cnpj=r[1] or "",
                    legal_name=r[0],
                    fund_type=r[2],
                    investment_class=r[3],
                )
                for r in rows
            ]
            return results
        except Exception as e:
            print(f"Error in search_performance: {e}")
            return []
