"""
Unit tests for IntentClassifier module.

Tests intent classification logic. Mocks LLM calls to avoid expensive API calls.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
class TestIntentClassifier:
    """Unit tests for IntentClassifier."""

    @patch("src.agent.fund_search.modules.intent.dspy.Predict")
    def test_initialization(self, mock_predict):
        """Test IntentClassifier initializes correctly."""
        from src.agent.fund_search.modules.intent import IntentClassifier

        classifier = IntentClassifier()
        assert classifier is not None

    @pytest.mark.skip(reason="DSPy module testing requires complex mocking - covered by e2e tests")
    def test_classify_returns_intent(self):
        """Test classify method returns intent."""
        pass

    @patch("src.agent.fund_search.modules.intent.dspy.Predict")
    def test_classify_with_different_queries(self, mock_predict, sample_queries):
        """Test classification with various query types."""
        from src.agent.fund_search.modules.intent import IntentClassifier

        classifier = IntentClassifier()

        # Just test that it can be called with different queries
        for query_type, query in sample_queries.items():
            # Mock response
            mock_response = Mock()
            mock_response.intents = [query_type]
            mock_predict.return_value = Mock(forward=Mock(return_value=mock_response))

            result = classifier.classify(query=query)
            assert result is not None


@pytest.mark.integration
@pytest.mark.requires_llm
class TestIntentClassifierIntegration:
    """
    Integration tests for IntentClassifier with real LLM calls.

    These tests make actual LLM API calls and are expensive.
    Only run when you want to validate actual intent classification.
    """

    @pytest.mark.skip(reason="Covered by e2e tests")
    def test_classify_find_by_name(self):
        """Test classification of find_by_name queries."""
        pass
