import dspy

from src.agent.models.query import NumericFilter, ParsedQuery
from src.agent.signatures.extraction import (
    ExtractCriteriaSignature,
    ExtractExposureSignature,
    ExtractNumericSignature,
)


class SpecializedExtractor(dspy.Module):
    """
    Module that runs specific extractors based on detected intents.

    INTENT → EXTRACTION MAPPING:
    - find_by_name/find_by_strategy → Use optimized search_query from intent classification
    - find_by_criteria → extract structured filters (for FundSearchTool)
    - find_by_exposure → extract asset holdings (for PositionSearchTool)
    - has_numeric_filter → extract numeric filter (for SnapshotSearchTool/PerformanceSearchTool)
    """

    def __init__(self):
        super().__init__()
        self.extract_criteria = dspy.ChainOfThought(ExtractCriteriaSignature)
        self.extract_exposure = dspy.ChainOfThought(ExtractExposureSignature)
        self.extract_numeric = dspy.ChainOfThought(ExtractNumericSignature)

    def forward(
        self,
        query: str,
        intents: list[str],
        language: str = "pt",
        search_query: str | None = None,
        required_name_terms: list[str] | None = None,
    ) -> dspy.Prediction:
        """
        Run relevant extractors based on intents.

        Args:
            query: Original user query
            intents: List of detected intents
            language: Detected language
            search_query: Optimized search query from intent classification (for semantic search)
            required_name_terms: List of terms that MUST appear in the fund name (from intent)
        """
        parsed = ParsedQuery(query=query, intents=intents, detected_language=language)

        # 1. Semantic Search: find_by_name or find_by_strategy
        if "find_by_name" in intents or "find_by_strategy" in intents:
            parsed.semantic_query = search_query or query
            parsed.required_name_terms = required_name_terms

            # Run structured extraction to identify potential filters (e.g. manager name)
            # even if the primary intent is semantic.
            criteria_result = self.extract_criteria(query=query)
            parsed.service_provider_entity = criteria_result.service_provider_entity
            parsed.fund_type = criteria_result.fund_type
            parsed.investment_class = criteria_result.investment_class

        # 2. Structured Criteria: find_by_criteria
        if "find_by_criteria" in intents:
            criteria_result = self.extract_criteria(query=query)
            parsed.fund_type = criteria_result.fund_type
            parsed.investment_class = criteria_result.investment_class
            parsed.target_audience = criteria_result.target_audience
            parsed.service_provider_entity = criteria_result.service_provider_entity
            parsed.fund_of_funds = criteria_result.fund_of_funds
            parsed.manager_type = criteria_result.manager_type
            parsed.is_exclusive_fund = criteria_result.is_exclusive_fund
            parsed.can_invest_abroad_100_pct = criteria_result.can_invest_abroad_100_pct
            parsed.has_long_term_taxation = criteria_result.has_long_term_taxation

        # 3. Exposure: find_by_exposure
        if "find_by_exposure" in intents:
            exposure_result = self.extract_exposure(query=query)
            parsed.asset_name = exposure_result.asset_name
            parsed.asset_tickers = exposure_result.asset_tickers
            parsed.asset_type = exposure_result.asset_type

        # 4. Numeric Filter: has_numeric_filter
        if "has_numeric_filter" in intents:
            numeric_result = self.extract_numeric(query=query)
            parsed.numeric_filter = NumericFilter(
                metric=numeric_result.metric,
                operator=numeric_result.operator,
                value=numeric_result.value,
                max_value=numeric_result.max_value,
                top_n=numeric_result.top_n,
                benchmark_name=numeric_result.benchmark_name,
                performance_period=numeric_result.performance_period,
                original_text=query,
            )

        # 5. Follow-up flag
        if "general_browse" in intents:
            parsed.needs_followup = True

        return dspy.Prediction(parsed_query=parsed)
