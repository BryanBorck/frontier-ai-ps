"""
Unit tests for SpecializedExtractor module.

Tests criteria extraction logic. Mocks LLM calls.
"""

import pytest
from unittest.mock import Mock, patch
from src.agent.fund_search.models.query import ParsedQuery, FundSearchCriteria


@pytest.mark.unit
class TestSpecializedExtractor:
    """Unit tests for SpecializedExtractor."""

    @patch('src.agent.fund_search.modules.extraction.dspy.ChainOfThought')
    def test_initialization(self, mock_cot):
        """Test SpecializedExtractor initializes correctly."""
        from src.agent.fund_search.modules.extraction import SpecializedExtractor

        extractor = SpecializedExtractor()
        assert extractor is not None

    @patch('src.agent.fund_search.modules.extraction.dspy.ChainOfThought')
    def test_extract_returns_parsed_query(self, mock_cot):
        """Test extract method returns ParsedQuery."""
        from src.agent.fund_search.modules.extraction import SpecializedExtractor

        # Mock the extraction result
        mock_result = Mock()
        mock_result.investment_class = "Ações"
        mock_result.fund_type = "FI"
        mock_result.target_audience = None
        mock_cot.return_value = Mock(forward=Mock(return_value=mock_result))

        extractor = SpecializedExtractor()
        result = extractor.extract(
            query="Fundos de ações",
            intent="find_by_criteria"
        )

        assert isinstance(result, ParsedQuery)
        assert isinstance(result.criteria, FundSearchCriteria)

    @patch('src.agent.fund_search.modules.extraction.dspy.ChainOfThought')
    def test_extract_with_context(self, mock_cot):
        """Test extraction with conversation context."""
        from src.agent.fund_search.modules.extraction import SpecializedExtractor
        from src.agent.fund_search.models.query import FundSearchCriteria

        mock_result = Mock()
        mock_result.investment_class = "Renda Fixa"
        mock_cot.return_value = Mock(forward=Mock(return_value=mock_result))

        extractor = SpecializedExtractor()

        # Previous context
        accumulated = FundSearchCriteria(fund_type=["FII"])

        result = extractor.extract(
            query="Quero ver apenas de renda fixa",
            intent="find_by_criteria",
            accumulated_criteria=accumulated
        )

        assert isinstance(result, ParsedQuery)

    @patch('src.agent.fund_search.modules.extraction.dspy.ChainOfThought')
    def test_extract_handles_empty_query(self, mock_cot):
        """Test extraction handles empty query gracefully."""
        from src.agent.fund_search.modules.extraction import SpecializedExtractor

        mock_result = Mock()
        mock_result.investment_class = None
        mock_cot.return_value = Mock(forward=Mock(return_value=mock_result))

        extractor = SpecializedExtractor()
        result = extractor.extract(query="", intent="find_by_criteria")

        assert isinstance(result, ParsedQuery)


@pytest.mark.integration
@pytest.mark.requires_llm
class TestSpecializedExtractorIntegration:
    """
    Integration tests with real LLM calls.

    These tests validate actual extraction behavior.
    """

    def test_extract_investment_class(self):
        """Test extraction of investment class."""
        from src.agent.fund_search.modules.extraction import SpecializedExtractor

        extractor = SpecializedExtractor()
        result = extractor.extract(
            query="Fundos de ações para investidores qualificados",
            intent="find_by_criteria"
        )

        assert result.criteria.investment_class is not None
        assert "Ações" in result.criteria.investment_class

    def test_extract_numeric_filters(self):
        """Test extraction of numeric filters."""
        from src.agent.fund_search.modules.extraction import SpecializedExtractor

        extractor = SpecializedExtractor()
        result = extractor.extract(
            query="Fundos com AUM acima de 100 milhões",
            intent="find_by_criteria"
        )

        # Should extract numeric filter
        assert result.criteria.numeric_filters is not None
