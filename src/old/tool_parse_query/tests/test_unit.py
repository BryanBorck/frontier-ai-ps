"""Unit tests for tool_parse_query."""

import os

import pytest

from src.tools.tool_parse_query.index import tool_parse_query
from src.tools.tool_parse_query.module_pipeline import (
    FundSearchCriteria,
    ParseQueryModule,
)


@pytest.fixture
def parser():
    """Create parser module with OpenAI API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    import dspy
    dspy.configure(lm=dspy.LM(model="openai/gpt-4.1-mini", api_key=api_key))

    return ParseQueryModule()


class TestFundSearchCriteria:
    """Test FundSearchCriteria model."""

    def test_create_empty_criteria(self):
        """Test creating criteria with all None values."""
        criteria = FundSearchCriteria()
        assert criteria.fund_legal_name is None
        assert criteria.fund_type is None
        assert criteria.investment_class is None
        assert criteria.fund_of_funds is None

    def test_create_criteria_with_fund_type(self):
        """Test creating criteria with fund_type."""
        criteria = FundSearchCriteria(fund_type="FIP")
        assert criteria.fund_type == "FIP"
        assert criteria.fund_legal_name is None

    def test_create_criteria_with_all_fields(self):
        """Test creating criteria with all fields."""
        criteria = FundSearchCriteria(
            fund_legal_name="BTG",
            fund_type="FIP",
            investment_class="Multimercado",
            fund_of_funds=True,
        )
        assert criteria.fund_legal_name == "BTG"
        assert criteria.fund_type == "FIP"
        assert criteria.investment_class == "Multimercado"
        assert criteria.fund_of_funds is True

    def test_model_dump(self):
        """Test model_dump returns dict."""
        criteria = FundSearchCriteria(fund_type="FIP")
        result = criteria.model_dump()
        assert isinstance(result, dict)
        assert result["fund_type"] == "FIP"


class TestParseQueryModule:
    """Test ParseQueryModule."""

    def test_parse_fund_type_fip(self, parser):
        """Test parsing query for FIP funds."""
        result = parser("find FIP funds")
        assert isinstance(result, FundSearchCriteria)
        assert result.fund_type == "FIP"

    def test_parse_fund_type_fidc(self, parser):
        """Test parsing query for FIDC funds."""
        result = parser("show me FIDC funds")
        assert result.fund_type == "FIDC"

    def test_parse_fund_name(self, parser):
        """Test parsing query with fund name."""
        result = parser("find funds with BTG in the name")
        assert result.fund_legal_name is not None
        assert "btg" in result.fund_legal_name.lower()

    def test_parse_investment_class(self, parser):
        """Test parsing query with investment class."""
        result = parser("show me Multimercado funds")
        assert result.investment_class == "Multimercado"

    def test_parse_returns_criteria(self, parser):
        """Test that parse returns FundSearchCriteria."""
        result = parser("any query")
        assert isinstance(result, FundSearchCriteria)


class TestToolParseQuery:
    """Test tool_parse_query function."""

    def test_tool_parse_query_success(self):
        """Test tool_parse_query with valid input."""
        result = tool_parse_query({"query": "find FIP funds"})
        assert isinstance(result, dict)
        assert "fund_type" in result
        assert "fund_legal_name" in result
        assert "investment_class" in result
        assert "fund_of_funds" in result

    def test_tool_parse_query_missing_query(self):
        """Test tool_parse_query with missing query field."""
        with pytest.raises(ValueError, match="Missing required field 'query'"):
            tool_parse_query({})

    def test_tool_parse_query_returns_dict(self):
        """Test tool_parse_query returns dictionary."""
        result = tool_parse_query({"query": "any query"})
        assert isinstance(result, dict)
