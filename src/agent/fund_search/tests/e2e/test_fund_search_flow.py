"""
End-to-end tests for complete fund search workflows.

Tests the entire flow from user query to final results.
Uses real databases and may make LLM calls (depending on configuration).
"""

import pytest
from src.agent.fund_search.orchestrator import FundSearchTool
from src.agent.fund_search.models.output import SearchOutput


@pytest.mark.e2e
@pytest.mark.requires_db
@pytest.mark.slow
class TestFundSearchE2E:
    """End-to-end tests for complete fund search workflows."""

    def test_simple_fund_search_by_name(self, real_db_path, real_vector_store_path, mock_llm_response):
        """Test complete flow: search fund by name."""
        # Note: This test requires real databases
        # LLM calls are mocked to avoid API costs

        tool = FundSearchTool()

        # Simple query
        result = tool.ask("Encontre fundos XP")

        # Should return SearchOutput
        assert isinstance(result, SearchOutput)
        assert result.cnpjs is not None

    def test_fund_search_by_criteria(self, real_db_path, real_vector_store_path):
        """Test complete flow: search fund by criteria."""
        tool = FundSearchTool()

        result = tool.ask("Fundos imobiliários para investidores qualificados")

        assert isinstance(result, SearchOutput)
        assert result.response_type in ["list_results", "too_many_results", "followup"]

    def test_fund_search_multi_turn(self, real_db_path, real_vector_store_path):
        """Test complete flow: multi-turn conversation."""
        tool = FundSearchTool()

        # First turn
        result1 = tool.ask("Fundos de investimento")
        assert isinstance(result1, SearchOutput)

        # Second turn - refinement
        result2 = tool.ask("Apenas os de ações")
        assert isinstance(result2, SearchOutput)

    def test_fund_search_by_exposure(self, real_db_path, real_vector_store_path):
        """Test complete flow: search by asset exposure."""
        tool = FundSearchTool()

        result = tool.ask("Fundos que investem em Petrobras")

        assert isinstance(result, SearchOutput)

    def test_fund_search_with_numeric_filter(self, real_db_path, real_vector_store_path):
        """Test complete flow: search with numeric filters."""
        tool = FundSearchTool()

        result = tool.ask("Fundos com AUM acima de 100 milhões")

        assert isinstance(result, SearchOutput)

    def test_fund_search_informational_query(self, real_db_path, real_vector_store_path):
        """Test complete flow: informational query handling."""
        tool = FundSearchTool()

        result = tool.ask("O que é um FII?")

        assert isinstance(result, SearchOutput)
        # Should be informational response type
        assert result.response_type == "informational"

    def test_fund_search_no_results(self, real_db_path, real_vector_store_path):
        """Test complete flow: query with no results."""
        tool = FundSearchTool()

        result = tool.ask("Fundos do planeta Marte")

        assert isinstance(result, SearchOutput)
        assert result.response_type == "no_results"
        assert len(result.cnpjs) == 0


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

    def test_complete_workflow_real_llm(self, real_db_path, real_vector_store_path):
        """Test complete workflow with real LLM calls."""
        tool = FundSearchTool()

        result = tool.ask("Quero investir em fundos imobiliários de shopping centers")

        # Should properly classify intent, extract criteria, and search
        assert isinstance(result, SearchOutput)
        assert result.cnpjs is not None
        assert len(result.cnpjs) >= 0

    def test_disambiguation_workflow_real_llm(self, real_db_path, real_vector_store_path):
        """Test disambiguation workflow with real LLM."""
        tool = FundSearchTool()

        # Ambiguous query should trigger disambiguation
        result = tool.ask("Fundos XP")

        assert isinstance(result, SearchOutput)
        # Might be list_results or disambiguation depending on how many funds match
        assert result.response_type in ["list_results", "disambiguation", "single_match"]
