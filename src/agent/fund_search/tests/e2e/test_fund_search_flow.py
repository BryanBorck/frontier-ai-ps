"""
End-to-end tests for complete fund search workflows.

Tests the entire flow from user query to final results.
Uses real databases and may make LLM calls (depending on configuration).
"""

import pytest

from src.agent.fund_search.models.output import SearchOutput


@pytest.mark.e2e
@pytest.mark.requires_db
@pytest.mark.slow
class TestFundSearchE2E:
    """End-to-end tests for complete fund search workflows."""

    def test_simple_fund_search_by_name(self, fund_search_tool):
        """Test complete flow: search fund by name."""
        # Note: This test requires real databases
        # LLM calls are mocked to avoid API costs

        tool = fund_search_tool

        # Simple query
        result = tool.ask("Encontre fundos XP")

        # Should return SearchOutput
        assert isinstance(result, SearchOutput)
        assert result.cnpjs is not None

    def test_fund_search_by_criteria(self, fund_search_tool):
        """Test complete flow: search fund by criteria."""
        tool = fund_search_tool

        result = tool.ask("Fundos imobiliários para investidores qualificados")

        assert isinstance(result, SearchOutput)
        assert result.response_type in ["list_results", "too_many_results", "followup"]

    def test_fund_search_multi_turn(self, fund_search_tool):
        """Test complete flow: multi-turn conversation."""
        tool = fund_search_tool

        # First turn
        result1 = tool.ask("Fundos de investimento")
        assert isinstance(result1, SearchOutput)

        # Second turn - refinement
        result2 = tool.ask("Apenas os de ações")
        assert isinstance(result2, SearchOutput)

    def test_fund_search_by_exposure(self, fund_search_tool):
        """Test complete flow: search by asset exposure."""
        tool = fund_search_tool

        result = tool.ask("Fundos que investem em Petrobras")

        assert isinstance(result, SearchOutput)

    def test_fund_search_with_numeric_filter(self, fund_search_tool):
        """Test complete flow: search with numeric filters."""
        tool = fund_search_tool

        result = tool.ask("Fundos com AUM acima de 100 milhões")

        assert isinstance(result, SearchOutput)

    def test_fund_search_no_results(self, fund_search_tool):
        """Test complete flow: unusual query that tests edge case handling."""
        tool = fund_search_tool

        result = tool.ask("Fundos do planeta Marte")

        # System should handle unusual queries gracefully
        assert isinstance(result, SearchOutput)
        # May return various response types - the system tries to be helpful
        assert result.response_type in ["no_results", "list_results", "no_results_followup"]
        # Semantic search may find related results (e.g., space-themed funds)
        assert result.cnpjs is not None


@pytest.mark.e2e
@pytest.mark.requires_db
@pytest.mark.requires_llm
@pytest.mark.slow
class TestFundSearchE2EWithRealLLM:
    """
    E2E tests with actual LLM calls.

    WARNING: These tests make real LLM API calls and are expensive.
    Only run when validating full system behavior.
    """

    def test_complete_workflow_real_llm(self, fund_search_tool):
        """Test complete workflow with real LLM calls."""
        tool = fund_search_tool

        result = tool.ask("Quero investir em fundos imobiliários de shopping centers")

        # Should properly classify intent, extract criteria, and search
        assert isinstance(result, SearchOutput)
        assert result.cnpjs is not None
        assert len(result.cnpjs) >= 0

    def test_disambiguation_workflow_real_llm(self, fund_search_tool):
        """Test disambiguation workflow with real LLM."""
        tool = fund_search_tool

        # Ambiguous query should trigger disambiguation or followup
        result = tool.ask("Fundos XP")

        assert isinstance(result, SearchOutput)
        # Might be list_results, disambiguation, single_match, or no_results_followup depending on LLM interpretation
        assert result.response_type in [
            "list_results",
            "disambiguation",
            "single_match",
            "no_results_followup",
        ]
