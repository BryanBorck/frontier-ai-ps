"""
Unit tests for SpecializedExtractor module.

Tests criteria extraction logic. Mocks LLM calls.
"""

from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestSpecializedExtractor:
    """Unit tests for SpecializedExtractor."""

    @patch("src.agent.fund_search.modules.extraction.dspy.ChainOfThought")
    def test_initialization(self, mock_cot):
        """Test SpecializedExtractor initializes correctly."""
        from src.agent.fund_search.modules.extraction import SpecializedExtractor

        extractor = SpecializedExtractor()
        assert extractor is not None

    @pytest.mark.skip(reason="DSPy module testing requires complex mocking - covered by e2e tests")
    def test_extract_returns_parsed_query(self):
        """Test extract method returns ParsedQuery."""
        pass

    @pytest.mark.skip(reason="DSPy module testing requires complex mocking - covered by e2e tests")
    def test_extract_with_context(self):
        """Test extraction with conversation context."""
        pass

    @pytest.mark.skip(reason="DSPy module testing requires complex mocking - covered by e2e tests")
    def test_extract_handles_empty_query(self):
        """Test extraction handles empty query gracefully."""
        pass


@pytest.mark.integration
@pytest.mark.requires_llm
class TestSpecializedExtractorIntegration:
    """
    Integration tests with real LLM calls.

    These tests validate actual extraction behavior.
    """

    @pytest.mark.skip(reason="Covered by e2e tests")
    def test_extract_investment_class(self):
        """Test extraction of investment class."""
        pass

    @pytest.mark.skip(reason="Covered by e2e tests")
    def test_extract_numeric_filters(self):
        """Test extraction of numeric filters."""
        pass
