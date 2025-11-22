"""Integration tests for tool_search_db."""

import os

import pytest

from src.tools.tool_parse_query.module_pipeline import ParseQueryModule
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


class TestSearchDBIntegration:
    """Integration tests for search_db with parser."""

    def test_parse_and_search(self, parser):
        """Test complete flow with structured output."""
        criteria = parser("find FIDC funds")
        results = search_funds(criteria, limit=3)

        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 3

        for fund in results:
            assert fund.legal_name is not None
            assert fund.cnpj is not None
            assert fund.fund_type == "FIDC"
