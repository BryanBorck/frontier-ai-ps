"""End-to-end tests for the complete agent flow."""

import os

import pytest

from src.agent.orchestrator import FundSearchOrchestrator


@pytest.fixture
def agent():
    """Create orchestrator instance with OpenAI API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    return FundSearchOrchestrator(api_key=api_key)


class TestAgentE2E:
    """End-to-end tests for the complete agent."""

    def test_agent_find_fip_funds(self, agent):
        """Test agent finding FIP funds."""
        answer = agent.ask("find FIP funds")

        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "FIP" in answer or "funds" in answer.lower()

    def test_agent_find_funds_by_name(self, agent):
        """Test agent finding funds by name."""
        answer = agent.ask("show me funds with Vinci in the name")

        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "vinci" in answer.lower() or "funds" in answer.lower()

    def test_agent_trajectory_tracking(self, agent):
        """Test that agent tracks tool usage."""
        agent.ask("find FIDC funds")
        result = agent.get_last_result()

        assert result is not None
        assert hasattr(result, "trajectory")
        assert isinstance(result.trajectory, dict)

    def test_agent_conversation_history(self, agent):
        """Test conversation history management."""
        agent.chat("find FIP funds")
        agent.chat("show me FIDC funds")

        history = agent.get_history()
        assert len(history) == 2
        assert history[0]["question"] == "find FIP funds"
        assert history[1]["question"] == "show me FIDC funds"

    def test_agent_reset_history(self, agent):
        """Test resetting conversation history."""
        agent.chat("find FIP funds")
        agent.reset_history()

        history = agent.get_history()
        assert len(history) == 0

    def test_agent_multiple_queries(self, agent):
        """Test agent handling multiple different queries."""
        queries = [
            "find FIP funds",
            "show me FIDC funds",
            "funds with BTG in the name",
        ]

        for query in queries:
            answer = agent.ask(query)
            assert isinstance(answer, str)
            assert len(answer) > 0
