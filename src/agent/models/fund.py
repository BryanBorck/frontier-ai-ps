from typing import Literal

from pydantic import BaseModel, Field


class FundResult(BaseModel):
    """
    Standardized fund result model used across the application.
    Normalization target for all search sources (DB, Vector, API).
    """

    # REQUIRED - Always present (for merging)
    fund_id: str = Field(..., description="Unique identifier for the fund")
    cnpj: str = Field(..., description="CNPJ identifier")
    legal_name: str = Field(..., description="Full legal name of the fund")

    # OPTIONAL - Present based on search type/availability
    fund_type: str | None = Field(None, description="Fund type (FI, FIP, FIDC, etc.)")
    investment_class: str | None = Field(
        None, description="Investment class (Multimercado, Ações, etc.)"
    )
    target_audience: str | None = Field(None, description="Target audience type")

    # From snapshots (daily metrics)
    aum: float | None = Field(None, description="Net Asset Value (Patrimônio Líquido)")
    holders: int | None = Field(None, description="Number of cotistas")
    current_quota_value: float | None = Field(None, description="Current quota value")

    # From positions (holdings)
    position_value: float | None = Field(None, description="Value of specific position if relevant")
    asset_name: str | None = Field(None, description="Name of specific asset if relevant")

    # From semantic search
    match_score: float | None = Field(None, description="Similarity score (0.0 to 1.0)")
    description: str | None = Field(None, description="Fund description or strategy text")

    # Internal metadata
    last_updated: str | None = Field(None, description="Timestamp of data source")


class SearchResultItem(BaseModel):
    """
    Single result item with source tracking and merged scoring.
    Used for RRF (Reciprocal Rank Fusion) and disambiguation.
    """

    fund_id: str
    legal_name: str
    cnpj: str

    # Source tracking
    source: Literal["semantic", "structured", "both"]
    semantic_score: float | None = None  # 0.0-1.0 similarity
    structured_rank: int | None = None  # Position in structured results

    # Combined score for ranking
    combined_score: float = 0.0

    # Additional context for user
    match_reason: str = Field(
        "", description="Explanation of why this fund matched (e.g., 'Exact name match')"
    )
    fund_details: FundResult | None = None  # Full details if available


class MergedSearchResults(BaseModel):
    """
    Container for results from multiple search paths.
    Includes metadata for disambiguation and follow-up logic.
    """

    items: list[SearchResultItem]

    # Statistics
    semantic_count: int = 0
    structured_count: int = 0
    both_count: int = 0  # Found by both sources

    # For disambiguation logic
    has_ambiguity: bool = False
    disambiguation_candidates: list[SearchResultItem] = []

    def get_top_results(self, limit: int = 10) -> list[SearchResultItem]:
        return self.items[:limit]
