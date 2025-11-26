"""
Unit tests for IntentClassifier module.

Tests intent classification logic. Mocks LLM calls to avoid expensive API calls.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestIntentClassifier:
    """Unit tests for IntentClassifier."""

    @patch('src.agent.fund_search.modules.intent.dspy.Predict')
    def test_initialization(self, mock_predict):
        """Test IntentClassifier initializes correctly."""
        from src.agent.fund_search.modules.intent import IntentClassifier

        classifier = IntentClassifier()
        assert classifier is not None

    @patch('src.agent.fund_search.modules.intent.dspy.Predict')
    def test_classify_returns_intent(self, mock_predict, sample_intent_response):
        """Test classify method returns intent."""
        from src.agent.fund_search.modules.intent import IntentClassifier

        # Mock the DSPy prediction
        mock_predict.return_value = Mock(forward=Mock(return_value=sample_intent_response))

        classifier = IntentClassifier()
        result = classifier.classify(query="Fundos de ações")

        assert hasattr(result, 'intent')
        assert result.intent == "find_by_criteria"

    @patch('src.agent.fund_search.modules.intent.dspy.Predict')
    def test_classify_with_different_queries(self, mock_predict, sample_queries):
        """Test classification with various query types."""
        from src.agent.fund_search.modules.intent import IntentClassifier

        classifier = IntentClassifier()

        # Just test that it can be called with different queries
        for query_type, query in sample_queries.items():
            # Mock response
            mock_response = Mock()
            mock_response.intent = query_type
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

    def test_classify_find_by_name(self):
        """Test classification of find_by_name queries."""
        from src.agent.fund_search.modules.intent import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify(query="Encontre o fundo XP Malls")

        assert result.intent in ["find_by_name", "find_by_criteria"]

    def test_classify_informational(self):
        """Test classification of informational queries."""
        from src.agent.fund_search.modules.intent import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify(query="O que é um FII?")

        assert result.intent == "informational"
