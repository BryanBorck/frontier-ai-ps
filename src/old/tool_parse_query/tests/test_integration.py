"""Integration tests for tool_parse_query."""

import os

import pytest

from src.tools.tool_parse_query.index import tool_parse_query
from src.tools.tool_parse_query.module_pipeline import FundSearchCriteria, ParseQueryModule
from src.tools.tool_search_db.module_pipeline import search_funds


@pytest.fixture
def parser():
    """Create parser module with OpenAI API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    import dspy
    dspy.configure(lm=dspy.LM(model="openai/gpt-4.1-mini", api_key=api_key))

    return ParseQueryModule()


class TestParseQueryIntegration:
    """Integration tests for parse_query with database."""

    def test_parse_and_search_fip(self, parser):
        """Test parsing FIP query and searching database."""
        criteria = parser("find FIP funds")
        results = search_funds(criteria, limit=5)

        assert len(results) > 0
        assert all(fund.fund_type == "FIP" for fund in results)

    def test_parse_and_search_fund_name(self, parser):
        """Test parsing fund name query and searching."""
        criteria = parser("show me funds with Vinci in the name")
        results = search_funds(criteria, limit=5)

        assert len(results) > 0
        assert all("vinci" in fund.legal_name.lower() for fund in results)

    def test_tool_parse_query_integration(self):
        """Test tool_parse_query with full flow."""
        result = tool_parse_query({"query": "find FIP funds"})

        assert isinstance(result, dict)
        assert result["fund_type"] == "FIP"

        # Use result to search
        criteria = FundSearchCriteria(**result)
        funds = search_funds(criteria, limit=5)
        assert len(funds) > 0
