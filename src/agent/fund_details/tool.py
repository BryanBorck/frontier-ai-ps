import dspy
import duckdb

from src.agent.fund_search.models.fund import FundResult


class FundDetailsTool(dspy.Module):
    """
    Tool to retrieve detailed information for a list of funds by CNPJ.
    """

    def __init__(self, db_path: str = "src/infrastructure/database/br_funds.db"):
        super().__init__()
        self.db_path = db_path

    def forward(self, cnpjs: list[str]) -> list[FundResult]:
        """
        Get details for the provided list of CNPJs.
        """
        if not cnpjs:
            return []

        try:
            conn = duckdb.connect(self.db_path, read_only=True)

            # Escape CNPJs
            cnpjs_str = "', '".join(cnpjs)

            # Efficiently query by CNPJ using list_contains or UNNEST if possible,
            # but IN clause is fine for reasonable list sizes.
            # We need to extract CNPJ from the identifiers list to match.

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
                WHERE list_filter(identifiers, x -> x.type = 'CNPJ')[1].value IN ('{cnpjs_str}')
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            results = []
            for row in rows:
                results.append(
                    FundResult(
                        fund_id=str(row[0]),
                        cnpj=row[1] or "",
                        legal_name=row[2],
                        fund_type=row[3],
                        investment_class=row[4],
                        target_audience=row[5],
                        aum=row[6],
                    )
                )

            # Maintain order if possible (rank preservation)
            results_map = {r.cnpj: r for r in results}
            ordered_results = []
            for cnpj in cnpjs:
                if cnpj in results_map:
                    ordered_results.append(results_map[cnpj])

            return ordered_results

        except Exception as e:
            print(f"Error in FundDetailsTool: {e}")
            return []
