"""Tool: Parse Query

Parses natural language queries about Brazilian funds and extracts
structured search criteria.

Uses fast regex-based parsing for common patterns (~1ms), falls back to
LLM parsing for complex queries (~4s).
"""

from .fast_parser import fast_parse
from .module_pipeline import FundSearchCriteria, ParseQueryModule, execute


def tool_parse_query(input_data: dict) -> dict:
    """Main tool entry point for parsing fund queries.

    Input schema (from schema.json):
        { "query": string }

    Output schema (from schema.json):
        {
          "fund_legal_name": string | null,
          "fund_type": string | null,
          "investment_class": string | null,
          "fund_of_funds": boolean | null
        }

    Args:
        input_data: Dictionary with 'query' key

    Returns:
        Dictionary with extracted fund search criteria

    Raises:
        ValueError: If 'query' field is missing
    """
    query = input_data.get("query")
    if query is None:
        raise ValueError("Missing required field 'query'")

    # Try fast path first (regex patterns)
    criteria = fast_parse(query)
    if criteria:
        return criteria.model_dump()

    # Fall back to LLM parsing for complex queries
    return execute(query=query)


class _FundQueryParserInternal:
    """Internal parser for ReAct agent compatibility.

    This class is not part of the public tool API.
    Use tool_parse_query() for the standard tool interface.

    Uses fast regex-based parsing for common patterns, falls back to LLM.
    """

    def __init__(self):
        self.module = ParseQueryModule()

    def parse(self, query: str) -> FundSearchCriteria:
        """Parse query and return FundSearchCriteria object.

        Fast path (regex): ~1ms for common patterns
        Slow path (LLM): ~4s for complex queries
        """
        # Try fast path first
        criteria = fast_parse(query)
        if criteria:
            return criteria

        # Fall back to LLM parsing
        return self.module(query=query)


# Export only the main tool function
__all__ = ["tool_parse_query"]
