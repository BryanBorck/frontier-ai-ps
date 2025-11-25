from typing import Literal

import dspy


class ExtractCriteriaSignature(dspy.Signature):
    """
    Extract filter criteria ONLY when EXPLICITLY mentioned by user.

    CRITICAL: Return None for any field NOT explicitly mentioned.
    Do NOT infer or assume default values!

    Examples:
    - "FIP funds" → fund_type=["FIP"], everything else=None
    - "funds for qualified investors" → target_audience=["QUALIFIED"], everything else=None
    - "multimercado funds" → investment_class=["Multimercado"], everything else=None
    - "bradesco gold fund" → everything=None (this is a name/strategy search, not criteria)
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
