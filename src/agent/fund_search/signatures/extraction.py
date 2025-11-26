from typing import Literal

import dspy


class ExtractCriteriaSignature(dspy.Signature):
    """
    You are a filter extraction assistant for investment fund queries. Your task is to extract ONLY filter criteria EXPLICITLY mentioned by the user in their query, strictly following the instructions below:

    GENERAL RULES:
    - For each field, RETURN None UNLESS it is EXPLICITLY stated in the query.
    - DO NOT infer, guess, or assume any criteria—even if they may seem implied or likely (e.g., don't extract "equity" for "ETF equity" unless "equity" is a defined filter field).
    - If the query is a fund name, nickname, or general search that does not clearly and explicitly mention filterable criteria, return None for all fields.
    - Only process and extract known filter fields described below; ignore all other attributes or details from the query.
    - Output ALL filter fields (even if None), and include a short reasoning for your output.

    FILTER FIELDS (return value types and explicit mention triggers):
    - fund_type (list of strings): Only if the query expressly mentions a fund type such as "FIP", "ETF", etc.
        - Examples: "FIP funds" → fund_type=["FIP"]
    - investment_class (list of strings): Only if the investment strategy/class is mentioned, e.g., "multimercado", "renda fixa", "ações".
        - Examples: "multimercado funds" → investment_class=["Multimercado"]
    - target_audience (list of strings): Only if the user specifies, e.g., "qualified investors", "general public".
        - Examples: "funds for qualified investors" → target_audience=["QUALIFIED"]
    - service_provider_entity (list of strings): Only if a service provider (e.g., bank, administrator) is mentioned AS a filter and not just in a fund name.
    - fund_of_funds (bool): Only if the query explicitly asks for funds that invest in other funds.
    - manager_type (list of strings): Only if a manager type (e.g., "bank manager", "independent manager") is stated as a filter.
    - is_exclusive_fund (bool): Only if exclusivity is mentioned ("exclusive fund").
    - can_invest_abroad_100_pct (bool): Only if the ability to invest 100% abroad is expressly requested.
        - Example: "Funds that can invest 100% abroad" → can_invest_abroad_100_pct=True
    - has_long_term_taxation (bool): Only if the query explicitly asks for long-term taxation.

    ADDITIONAL GUIDANCE:
    - Do NOT infer filters from keywords within fund/product names or types unless they match the above list and are clearly functioning as a filter.
        - Example: "bradesco gold fund" → all filters=None (this is a name/strategy search).
    - List and label every field, even if its value is None.

    OUTPUT FORMAT:
    - reasoning: State briefly which criteria (if any) were explicitly mentioned and mapped to fields, and confirm that no assumptions or inferences have been made.
    - For each filter field (as described above): show value or None.

    EXAMPLES:
    1. Query: "FIP funds"
       Output:
       reasoning: "User mentioned 'FIP', which maps explicitly to fund_type. No other criteria explicitly stated."
       fund_type=["FIP"]
       investment_class=None
       target_audience=None
       ... (other fields as None)

    2. Query: "Funds that can invest 100% abroad"
       Output:
       reasoning: "Explicit mention of ability to invest 100% abroad; all other fields not mentioned."
       fund_type=None
       investment_class=None
       target_audience=None
       can_invest_abroad_100_pct=True
       ... (other fields as None)

    3. Query: "bradesco value"
       Output:
       reasoning: "No explicit filter criteria stated; likely a fund name search."
       fund_type=None
       investment_class=None
       ... (all fields as None)

    STRICTLY AVOID all inference and assumption—extract only what is plainly present, or return None.
    """

    query: str = dspy.InputField(desc="User query containing categorical filters")

    fund_type: (
        list[
            Literal[
                "FI",
                "FIP",
                "FIDC",
                "FII",
                "ETF",
                "CLASSES - FIF",
                "CLASSES - FIP",
                "FACFIF",
                "FIF",
                "FITVM",
            ]
        ]
        | None
    ) = dspy.OutputField(
        desc="""ONLY extract if user explicitly mentions fund type (FI, FIP, FIDC, FII, ETF).
        Return None if not mentioned."""
    )

    investment_class: (
        list[
            Literal[
                "Multimercado",
                "Ações",
                "Renda Fixa",
                "Cambial",
                "Dívida Externa",
                "Referenciado",
                "Curto Prazo",
                "FIP",
                "FII",
            ]
        ]
        | None
    ) = dspy.OutputField(
        desc="""ONLY extract if user explicitly mentions investment class.
        Return None if not mentioned."""
    )

    target_audience: list[Literal["PROFESSIONAL", "QUALIFIED", "RETAIL"]] | None = dspy.OutputField(
        desc="""ONLY if user mentions investor type (qualified, professional, retail).
        Return None if not mentioned."""
    )

    service_provider_entity: list[str] | None = dspy.OutputField(
        desc="""Extract manager/admin name if explicitly mentioned in the query.
        Examples:
        - "bradesco gold fund" → ["Bradesco"]
        - "safra funds" → ["Safra"]
        - "itau tech" → ["Itau"]"""
    )

    fund_of_funds: bool | None = dspy.OutputField(
        desc="True ONLY if user explicitly mentions 'fund of funds', 'FIC', or 'FoF'. Otherwise None."
    )

    manager_type: list[Literal["CORPORATE", "INDIVIDUAL"]] | None = dspy.OutputField(
        desc="""ONLY extract if user explicitly asks for corporate vs individual managers.
        Return None if not mentioned."""
    )

    is_exclusive_fund: bool | None = dspy.OutputField(
        desc="True ONLY if user explicitly mentions 'exclusive' or 'restricted' funds. Otherwise None."
    )

    can_invest_abroad_100_pct: bool | None = dspy.OutputField(
        desc="True ONLY if user mentions investing 100% abroad. Otherwise None."
    )

    has_long_term_taxation: bool | None = dspy.OutputField(
        desc="True ONLY if user mentions long-term taxation benefits. Otherwise None."
    )


class ExtractExposureSignature(dspy.Signature):
    """
    Extract asset exposure criteria for finding funds that HOLD specific assets.

    Examples:
    - "funds holding Petrobras" → asset_name=["Petrobras"], asset_tickers=["PETR3", "PETR4"]
    - "exposure to Vale" → asset_name=["Vale"], asset_tickers=["VALE3"]
    - "funds with NVDA" → asset_tickers=["NVDA34", "NVDA"]
    """

    query: str = dspy.InputField(desc="User query asking about asset holdings")

    asset_name: list[str] | None = dspy.OutputField(
        desc="List of company or asset names (e.g., ['Petrobras', 'Vale'])"
    )

    asset_tickers: list[str] | None = dspy.OutputField(
        desc="Specific tickers if mentioned or INFERRED from common stocks (e.g., PETR4, VALE3)"
    )

    asset_type: (
        list[
            Literal[
                "EQUITY",
                "FIXED_INCOME",
                "INVESTMENT_FUND",
                "DERIVATIVES",
                "CASH",
            ]
        ]
        | None
    ) = dspy.OutputField(
        desc="""Type of asset held by the fund.
        - EQUITY: Stocks, Shares
        - FIXED_INCOME: Bonds, Debentures
        - INVESTMENT_FUND: Fund quotas
        - DERIVATIVES: Options, Futures
        - CASH: Cash, Equivalents
        """
    )


class ExtractNumericSignature(dspy.Signature):
    """
    Extract numeric filter from natural language query.
    Handles Portuguese and English, various expressions.
    """

    query: str = dspy.InputField(desc="Natural language query in Portuguese or English")

    metric: Literal[
        "aum", "holders", "return", "position_value", "management_fee", "performance_fee"
    ] = dspy.OutputField(desc="What metric the user is filtering by")

    operator: Literal[
        "min",
        "max",
        "around",
        "top",
        "range",
        "exact",
    ] = dspy.OutputField(
        desc="""Normalized operator:
        - min: at least, pelo menos, greater than, maior que
        - max: at most, less than, menor que
        - around: approximately, cerca de
        - top: top N, maiores
        - range: between X and Y
        - exact: exactly
        """
    )

    value: float | None = dspy.OutputField(
        desc="Primary numeric value (normalized to base units, e.g., 200M → 200000000)"
    )

    max_value: float | None = dspy.OutputField(
        desc="Second value for range operator (between X and Y)"
    )

    top_n: int | None = dspy.OutputField(desc="N for 'top N' queries, default 10 if not specified")

    benchmark_name: Literal["IBOVESPA", "CDI", "SELIC"] | None = dspy.OutputField(
        desc="Benchmark name for comparison (e.g. IBOVESPA, CDI, SELIC)."
    )

    performance_period: Literal["1m", "3m", "6m", "12m", "24m", "36m", "ytd"] | None = (
        dspy.OutputField(
            desc="Period for performance comparison/filtering. Default to '12m' if implied."
        )
    )
