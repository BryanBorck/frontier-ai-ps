"""
Test that history clearing works correctly across MainAgent and FundSearchTool.

Verifies that when CLI calls reset_history(), both histories are cleared:
- MainAgent.history
- FundSearchTool.state.history
"""

import os

import pytest

from src.agent.main_agent import MainAgent


@pytest.fixture
def api_key():
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set")
    return key


@pytest.fixture
def main_agent(api_key):
    """Create MainAgent instance for testing."""
    return MainAgent(api_key=api_key, model="gpt-4o-mini")


@pytest.mark.unit
class TestHistoryClearing:
    """Test history clearing across MainAgent and FundSearchTool."""

    def test_reset_history_clears_both_histories(self, main_agent):
        """
        Test that reset_history() clears both:
        - MainAgent.history
        - FundSearchTool.state.history
        """
        # Manually populate both histories to simulate conversation
        # MainAgent history
        main_agent.history.append({"question": "Test question 1", "answer": "Test answer 1"})
        main_agent.history.append({"question": "Test question 2", "answer": "Test answer 2"})

        # FundSearchTool history (via update_history)
        main_agent.search_tool.update_history("Test question 1", "Test answer 1")
        main_agent.search_tool.update_history("Test question 2", "Test answer 2")

        # Verify both histories are populated
        assert len(main_agent.history) == 2
        assert len(main_agent.search_tool.state.history) == 2

        # Call reset_history() (same as CLI does)
        main_agent.reset_history()

        # Verify BOTH histories are cleared
        assert len(main_agent.history) == 0, "MainAgent.history should be cleared"
        assert (
            len(main_agent.search_tool.state.history) == 0
        ), "FundSearchTool.state.history should be cleared"

    def test_reset_history_clears_all_conversation_state(self, main_agent):
        """
        Test that reset_history() also clears other conversation state fields.
        """
        # Populate state
        main_agent.search_tool.state.turn = 5
        main_agent.search_tool.state.accumulated_criteria = {"investment_class": "EQUITY"}
        main_agent.search_tool.state.last_cnpjs = ["12345678000190", "98765432000100"]
        main_agent.search_tool.state.last_query = "Test query"
        main_agent.search_tool.state.history = [
            {"question": "Q1", "answer": "A1"},
            {"question": "Q2", "answer": "A2"},
        ]
        main_agent.search_tool.state.awaiting_clarification = True

        # Call reset_history()
        main_agent.reset_history()

        # Verify ALL state is cleared
        assert main_agent.search_tool.state.turn == 0
        assert main_agent.search_tool.state.accumulated_criteria == {}
        assert main_agent.search_tool.state.last_cnpjs == []
        assert main_agent.search_tool.state.last_query == ""
        assert main_agent.search_tool.state.history == []
        assert main_agent.search_tool.state.awaiting_clarification is False

    def test_get_history_returns_empty_after_reset(self, main_agent):
        """
        Test that get_history() returns empty list after reset.

        This is what the CLI uses to display history.
        """
        # Populate history
        main_agent.history.append({"question": "Test question", "answer": "Test answer"})

        # Verify history is populated
        history = main_agent.get_history()
        assert len(history) == 1

        # Reset
        main_agent.reset_history()

        # Verify get_history() returns empty
        history = main_agent.get_history()
        assert len(history) == 0
        assert history == []
