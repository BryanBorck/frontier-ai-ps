import dspy
import duckdb

from src.agent.fund_search.models.query import PositionSearchCriteria


class PositionSearchTool(dspy.Module):
    """
    Searches for funds based on their asset holdings/positions.

    NEW DESIGN PHILOSOPHY:
    - PRIMARY: Search by asset class (broad) - "funds investing in equities"
    - OPTIONAL: Refine by company names (narrow) - "funds investing in Petrobras equity"

    Examples:
    - Broad: "funds investing in equities" → asset_type=["EQUITY"]
    - Narrow: "funds investing in Petrobras" → asset_type=["EQUITY"], companies=["Petrobras"]
    - Mixed: "funds with Petrobras exposure" → companies=["Petrobras"] (all asset types)

    WHY this tool exists:
    - Users want to find funds by asset exposure (equities, fixed income, derivatives)
    - Company-level filtering is optional for deeper analysis
    - Aggregates exposure across all positions to rank funds by concentration
    """

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def forward(
        self,
        criteria: PositionSearchCriteria,
        cnpjs: list[str] | None = None,
        limit: int = 50,
    ) -> list[str]:
        """
        Search funds by their asset positions/holdings. Returns list of CNPJs.

        Args:
            criteria: PositionSearchCriteria with:
                - asset_type: PRIMARY FILTER - Asset classes (e.g., ["EQUITY"], ["FIXED_INCOME"])
                  WHY: Main use case is broad search by asset class
                  Examples: ["EQUITY"] for all equity funds, ["DERIVATIVES"] for derivative funds
                - companies: OPTIONAL REFINEMENT - Company names (e.g., ["Petrobras", "Vale"])
                  WHY: Narrow down to specific issuers
                  Examples: ["Petrobras"] for Petrobras-related assets only
            cnpjs: Optional list of CNPJs to filter search (pre-filtering from other tools)
            limit: Maximum number of results to return

        Returns:
            List of CNPJs sorted by total exposure (descending)

        Examples:
            - Broad search: criteria(asset_type=["EQUITY"]) → all equity funds
            - Narrow search: criteria(asset_type=["EQUITY"], companies=["Petrobras"]) → Petrobras equity
            - Company-only: criteria(companies=["Petrobras"]) → all Petrobras assets (stocks + derivatives)
        """
        try:
            conn = duckdb.connect(self.db_path, read_only=True)

            # 1. BUILD WHERE CLAUSE: Filter assets by criteria
            # NEW DESIGN: asset_type is PRIMARY, companies is OPTIONAL refinement

            asset_where_parts = []

            # PRIMARY FILTER: Asset class (EQUITY, FIXED_INCOME, DERIVATIVES, etc.)
            # WHY: Main use case is "funds investing in equities" (broad search)
            # Examples: asset_type=["EQUITY"] → all equity funds
            if criteria.asset_type:
                type_list = "', '".join(criteria.asset_type)
                asset_where_parts.append(f"a.asset_class IN ('{type_list}')")

            # OPTIONAL REFINEMENT: Filter by company names (issuer_name)
            # WHY: Deeper filtering like "Petrobras equity funds"
            # Examples: companies=["Petrobras", "Vale"] → only these issuers
            # Note: No ticker search - issuer_name partial matching is sufficient
            if criteria.companies:
                company_conditions = []
                for company in criteria.companies:
                    # Clean for SQL injection prevention
                    clean_company = company.replace("'", "''")
                    # Case-insensitive partial match on issuer name
                    company_conditions.append(f"a.issuer.issuer_name ILIKE '%{clean_company}%'")

                # Combine multiple companies with OR (find any of them)
                asset_where_parts.append(f"({' OR '.join(company_conditions)})")

            # Combine filters with AND
            # WHY: asset_type AND companies narrows the search
            # Example: ["EQUITY"] AND ["Petrobras"] → Petrobras stocks only
            asset_where = " AND ".join(asset_where_parts) if asset_where_parts else "1=1"

            # 2. OPTIONAL PRE-FILTERING: Filter by input CNPJs
            # WHY: If other tools already narrowed down the search, only look at those funds
            fund_filter = ""
            if cnpjs:
                cnpjs_str = "', '".join([cnpj.replace("'", "''") for cnpj in cnpjs])
                fund_filter = f"AND list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value IN ('{cnpjs_str}')"

            # 3. MAIN QUERY: Join positions with assets and funds
            # WHY: positions table links funds to assets with market values
            query = f"""
                WITH fund_exposures AS (
                    SELECT
                        f.fund_id,
                        list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value as cnpj,
                        a.issuer.issuer_name as issuer_name,
                        a.asset_class as asset_class,
                        SUM(p.current_market_value.value) as total_exposure
                    FROM positions p
                    -- Join to get asset details
                    JOIN assets a ON p.asset_id = a.asset_id
                    -- Join to get fund CNPJ
                    JOIN funds f ON p.fund_id = f.fund_id
                    WHERE {asset_where}
                      {fund_filter}
                      AND p.current_market_value.value IS NOT NULL
                    GROUP BY f.fund_id, cnpj, issuer_name, asset_class
                )
                SELECT
                    cnpj,
                    SUM(total_exposure) as total_fund_exposure
                FROM fund_exposures
                WHERE cnpj IS NOT NULL
                GROUP BY cnpj
                -- Order by total exposure (funds with highest concentration first)
                -- WHY: Users want funds most exposed to the target assets
                ORDER BY total_fund_exposure DESC
                LIMIT {limit}
            """

            rows = conn.execute(query).fetchall()
            conn.close()

            # Return list of CNPJs
            return [row[0] for row in rows if row[0]]

        except Exception as e:
            print(f"Error in search_positions: {e}")
            return []
