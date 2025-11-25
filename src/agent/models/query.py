from typing import Any, Literal

from pydantic import BaseModel, Field


class NumericFilter(BaseModel):
    """
    Flexible numeric filter extracted from natural language.
    Handles various operators and user expressions (e.g., 'at least', 'top 10').
    """

    metric: Literal[
        "aum", "holders", "return", "position_value", "management_fee", "performance_fee"
    ]

    # Normalized operator from natural language
    operator: Literal[
        "min",  # "at least", "minimum", "maior que"
        "max",  # "at most", "maximum", "menor que"
        "around",  # "around", "cerca de"
        "top",  # "top N", "maiores"
        "range",  # "between X and Y"
        "exact",  # "exactly"
    ]

    value: float | None = None
    max_value: float | None = None  # For range operator
    top_n: int | None = None  # For top operator

    benchmark_name: Literal["IBOVESPA", "CDI", "SELIC"] | None = None
    performance_period: Literal["1m", "3m", "6m", "12m", "24m", "36m", "ytd"] | None = None

    original_text: str | None = None  # The text that generated this filter


class FundSearchCriteria(BaseModel):
    """
    Structured criteria for fund metadata search.
    """

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
    ) = None

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
    ) = None

    target_audience: list[Literal["PROFESSIONAL", "QUALIFIED", "RETAIL"]] | None = None
    service_provider_entity: list[str] | None = None
    fund_of_funds: bool | None = None
    manager_type: list[Literal["CORPORATE", "INDIVIDUAL"]] | None = None
    is_exclusive_fund: bool | None = None
    can_invest_abroad_100_pct: bool | None = None
    has_long_term_taxation: bool | None = None

    def has_any_criteria(self) -> bool:
        """Check if any criteria field is set."""
        return any(
            [
                self.fund_type,
                self.investment_class,
                self.target_audience,
                self.service_provider_entity,
                self.fund_of_funds is not None,
                self.manager_type,
                self.is_exclusive_fund is not None,
                self.can_invest_abroad_100_pct is not None,
                self.has_long_term_taxation is not None,
            ]
        )


class PositionSearchCriteria(BaseModel):
    """
    Criteria for asset exposure search.
    """

    asset_name: list[str] | None = None
    asset_tickers: list[str] | None = None
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
    ) = None


class ParsedQuery(BaseModel):
    """
    Complete parsed query with all extracted information.
    Represents the agent's understanding of the user's intent.
    """

    # Original query context
    query: str
    detected_language: str = "pt"  # "pt" or "en"

    # Intents (can have multiple)
    intents: list[str] = Field(default_factory=list)

    # From ExtractName
    fund_name: str | None = None
    is_exact_match: bool = False

    # From ExtractCriteria
    fund_type: list[str] | None = None
    investment_class: list[str] | None = None
    target_audience: list[str] | None = None
    service_provider_entity: list[str] | None = None
    fund_of_funds: bool | None = None
    manager_type: list[str] | None = None
    is_exclusive_fund: bool | None = None
    can_invest_abroad_100_pct: bool | None = None
    has_long_term_taxation: bool | None = None

    # From ExtractExposure
    asset_name: list[str] | None = None
    asset_tickers: list[str] | None = None
    asset_type: list[str] | None = None

    # From ExtractNumeric
    numeric_filter: NumericFilter | None = None

    # For semantic search
    semantic_query: str | None = None
    required_name_terms: list[str] | None = None

    # Explicit context resolution (targeted lookup)
    targeted_fund_ids: list[str] | None = None

    # Conversation control
    needs_followup: bool = False

    def is_empty(self) -> bool:
        """Check if no meaningful criteria were extracted."""
        return not any(
            [
                self.fund_name,
                self.fund_type,
                self.investment_class,
                self.asset_name,
                self.asset_tickers,
                self.numeric_filter,
                self.semantic_query,
                self.service_provider_entity,
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class QuerySpecificity(BaseModel):
    """
    Measure of how specific/actionable a query is.
    Used to decide between searching immediately vs. asking clarifying questions.
    """

    score: float = Field(..., ge=0.0, le=1.0, description="0.0 (vague) to 1.0 (specific)")
    level: Literal["specific", "partial", "vague"]
    criteria_count: int
    suggested_followups: list[str] = Field(default_factory=list)

    def should_search_immediately(self) -> bool:
        return self.level in ["specific", "partial"]
