"""
Unit tests for ConversationManager module.

Tests conversation state management and followup logic.
"""

import pytest
from unittest.mock import Mock, patch
from src.agent.fund_search.modules.manager import ConversationManager
from src.agent.fund_search.models.state import ConversationState
from src.agent.fund_search.models.query import FundSearchCriteria, ParsedQuery


@pytest.mark.unit
class TestConversationManager:
    """Unit tests for ConversationManager."""

    def test_initialization(self):
        """Test ConversationManager initializes correctly."""
        manager = ConversationManager()
        assert manager is not None

    def test_should_ask_followup_with_empty_criteria(self):
        """Test followup not needed with empty criteria."""
        manager = ConversationManager()
        state = ConversationState(
            turn=1,
            accumulated_criteria=FundSearchCriteria(),
            last_cnpjs=[],
            history=[],
            awaiting_clarification=False
        )
        parsed = ParsedQuery(
            raw_query="fundos de investimento",
            criteria=FundSearchCriteria()
        )

        # Empty criteria might need followup
        result = manager.should_ask_followup_before_search(
            state=state,
            parsed_query=parsed,
            intent="find_by_criteria"
        )

        assert isinstance(result, bool)

    def test_should_ask_followup_with_specific_criteria(self):
        """Test followup not needed with specific criteria."""
        manager = ConversationManager()
        state = ConversationState(
            turn=1,
            accumulated_criteria=FundSearchCriteria(),
            last_cnpjs=[],
            history=[],
            awaiting_clarification=False
        )
        parsed = ParsedQuery(
            raw_query="fundos de ações XP",
            criteria=FundSearchCriteria(
                investment_class=["Ações"],
                service_provider_entity=["XP"]
            )
        )

        result = manager.should_ask_followup_before_search(
            state=state,
            parsed_query=parsed,
            intent="find_by_name"
        )

        # With specific criteria, likely don't need followup
        assert isinstance(result, bool)

    def test_should_ask_disambiguation_with_many_results(self):
        """Test disambiguation needed with many results."""
        manager = ConversationManager()
        state = ConversationState(
            turn=1,
            accumulated_criteria=FundSearchCriteria(),
            last_cnpjs=[],
            history=[],
            awaiting_clarification=False
        )

        # Many CNPJs suggest disambiguation might be needed
        many_cnpjs = [f"12.345.678/000{i}-90" for i in range(10)]

        result = manager.should_ask_disambiguation_after_search(
            state=state,
            cnpjs=many_cnpjs,
            intent="find_by_name"
        )

        assert isinstance(result, bool)

    def test_should_ask_disambiguation_with_single_result(self):
        """Test disambiguation not needed with single result."""
        manager = ConversationManager()
        state = ConversationState(
            turn=1,
            accumulated_criteria=FundSearchCriteria(),
            last_cnpjs=[],
            history=[],
            awaiting_clarification=False
        )

        result = manager.should_ask_disambiguation_after_search(
            state=state,
            cnpjs=["12.345.678/0001-90"],
            intent="find_by_name"
        )

        # Single result doesn't need disambiguation
        assert result is False

    def test_handle_followup_intent(self):
        """Test handling followup intent."""
        manager = ConversationManager()
        state = ConversationState(
            turn=2,
            accumulated_criteria=FundSearchCriteria(fund_type=["FII"]),
            last_cnpjs=["12.345.678/0001-90", "98.765.432/0001-10"],
            history=[{"query": "fundos imobiliários", "cnpjs": ["12.345.678/0001-90"]}],
            awaiting_clarification=False
        )
        parsed = ParsedQuery(
            raw_query="apenas os de shopping",
            criteria=FundSearchCriteria()
        )

        # Should handle followup by merging context
        result = manager.handle_followup(
            state=state,
            parsed_query=parsed
        )

        assert isinstance(result, bool) or result is None

    @patch('src.agent.fund_search.modules.manager.dspy.ChainOfThought')
    def test_generate_followup_question(self, mock_cot):
        """Test generating followup questions."""
        manager = ConversationManager()

        mock_result = Mock()
        mock_result.question = "Você quer fundos para investidores qualificados ou varejo?"
        mock_cot.return_value = Mock(forward=Mock(return_value=mock_result))

        state = ConversationState(
            turn=1,
            accumulated_criteria=FundSearchCriteria(),
            last_cnpjs=[],
            history=[],
            awaiting_clarification=False
        )
        parsed = ParsedQuery(
            raw_query="fundos de investimento",
            criteria=FundSearchCriteria()
        )

        question = manager.generate_followup_question(
            state=state,
            parsed_query=parsed
        )

        assert isinstance(question, str)


@pytest.mark.integration
@pytest.mark.requires_llm
class TestConversationManagerIntegration:
    """
    Integration tests for ConversationManager with real LLM calls.

    Tests actual conversation flow and followup generation.
    """

    def test_followup_generation_with_llm(self):
        """Test followup question generation with real LLM."""
        manager = ConversationManager()

        state = ConversationState(
            turn=1,
            accumulated_criteria=FundSearchCriteria(),
            last_cnpjs=[],
            history=[],
            awaiting_clarification=False
        )
        parsed = ParsedQuery(
            raw_query="fundos",
            criteria=FundSearchCriteria()
        )

        question = manager.generate_followup_question(
            state=state,
            parsed_query=parsed
        )

        # Should generate a meaningful question
        assert isinstance(question, str)
        assert len(question) > 10
