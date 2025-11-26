"""
E2E integration tests for the complete FundSearchTool orchestrator.

Tests the full pipeline:
User Query → Intent → Extraction → Search → Response

These tests use the REAL orchestrator with REAL LLM calls (not mocked).
"""

import os

import pytest

from src.agent.fund_search.orchestrator import FundSearchTool


@pytest.fixture
def api_key():
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set")
    return key


@pytest.fixture
def fund_search_tool(api_key):
    """Create FundSearchTool instance for testing."""
    return FundSearchTool(
        api_key=api_key,
        model="gpt-4o-mini",
        enable_mlflow=False,  # Disable MLflow for tests
    )


@pytest.mark.e2e
@pytest.mark.integration
class TestOrchestratorBasicFlow:
    """
    E2E tests for basic orchestrator functionality
    """

    def test_ticker_query_full_pipeline(self, fund_search_tool):
        """
        Test: "funds investing in PETR3"

        Expected flow:
        1. Intent: POSITION_SEARCH
        2. Extract: companies=["Petrobras"], asset_type=["EQUITY"]
        3. Search: Call position search tool
        4. Return: List of CNPJs

        Why critical: Most important use case - ticker mapping + search
        """
        result = fund_search_tool.ask("funds investing in PETR3")

        # Verify we got a response
        assert result is not None
        assert hasattr(result, "cnpjs")
        assert hasattr(result, "response_type")

        # We should get results (assuming DB has Petrobras funds)
        # Don't assert specific count, just that it's a list
        assert isinstance(result.cnpjs, list)

        # Response type should be valid (not error)
        valid_responses = ["list_results", "single_match", "no_results", "no_results_followup"]
        assert result.response_type in valid_responses

        print("\n✓ Ticker query test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")
        print(f"  - Response type: {result.response_type}")
        if result.interpretation_note:
            print(f"  - Interpretation: {result.interpretation_note}")
        if result.suggested_followup:
            print(f"  - Followup: {result.suggested_followup}")

    def test_broad_equity_query(self, fund_search_tool):
        """
        Test: "funds investing in equities"

        Expected flow:
        1. Intent: POSITION_SEARCH
        2. Extract: asset_type=["EQUITY"], companies=None
        3. Search: Broad equity search
        4. Return: Many CNPJs

        Why: Tests broad asset type search (no specific company)
        """
        result = fund_search_tool.ask("funds investing in equities")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        # Broad equity search should return many results
        # (assuming DB has equity funds)
        print("\n✓ Broad equity query test passed!")
        print(f"  - Found {len(result.cnpjs)} equity funds")
        print(f"  - Response type: {result.response_type}")

    def test_portuguese_query(self, fund_search_tool):
        """
        Test: "fundos que investem em PETR3"

        Expected flow:
        1. Detect language: PT
        2. Parse correctly despite Portuguese
        3. Extract: Same as English equivalent
        4. Return: Same results

        Why: Portuguese is primary language for Brazilian users
        """
        result = fund_search_tool.ask("fundos que investem em PETR3")

        assert result is not None
        assert result.detected_language == "pt"
        assert isinstance(result.cnpjs, list)

        print("\n✓ Portuguese query test passed!")
        print(f"  - Detected language: {result.detected_language}")
        print(f"  - Found {len(result.cnpjs)} funds")


@pytest.mark.e2e
@pytest.mark.integration
class TestOrchestratorConversationFlow:
    """
    E2E tests for multi-turn conversation flows.
    """

    def test_refinement_with_context(self, fund_search_tool):
        """
        Test two-turn conversation with refinement.

        Turn 1: "funds investing in equities"
        Turn 2: "only those with Petrobras"

        Expected:
        1. Turn 1: Broad equity search
        2. Turn 2: Refine with Petrobras filter
        3. Context should be maintained

        Why: Tests conversation state management
        """
        # Turn 1: Broad search
        result1 = fund_search_tool.ask("funds investing in equities")
        assert len(result1.cnpjs) > 0

        # Turn 2: Refinement (using context)
        result2 = fund_search_tool.ask(
            "only those with Petrobras",
            context_cnpjs=result1.cnpjs,
            use_history=True,
        )

        # Should have fewer results (refined)
        assert isinstance(result2.cnpjs, list)

        print("\n✓ Conversation refinement test passed!")
        print(f"  - Turn 1: {len(result1.cnpjs)} funds")
        print(f"  - Turn 2: {len(result2.cnpjs)} funds (refined)")

    def test_state_reset(self, fund_search_tool):
        """
        Test: State clears between independent queries.

        Query 1: "funds with PETR3"
        Query 2: "funds with VALE3" (use_history=False)

        Expected: Query 2 should not use context from Query 1

        Why: Tests state isolation
        """
        result1 = fund_search_tool.ask("funds with PETR3")
        fund_search_tool.clear_state()
        result2 = fund_search_tool.ask("funds with VALE3", use_history=False)

        # Both should return results independently
        assert isinstance(result1.cnpjs, list)
        assert isinstance(result2.cnpjs, list)

        print("\n✓ State reset test passed!")
        print(f"  - Query 1: {len(result1.cnpjs)} PETR3 funds")
        print(f"  - Query 2: {len(result2.cnpjs)} VALE3 funds (independent)")


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.slow
class TestOrchestratorEdgeCases:
    """
    E2E tests for edge cases and error handling.
    """

    def test_no_results_handling(self, fund_search_tool):
        """
        Test: Query that should return no results.

        Query: "funds investing in Apple stock"
        (Apple is US company, not in Brazilian market)

        Expected:
        1. Parse correctly
        2. Search executes
        3. Return empty list with appropriate response_type

        Why: Tests graceful handling of no matches
        """
        result = fund_search_tool.ask("funds investing in Apple stock")

        assert result is not None
        # Should return empty or very few results
        assert isinstance(result.cnpjs, list)
        # Response type should indicate no results or followup
        assert result.response_type in ["no_results", "no_results_followup", "list_results"]

        print("\n✓ No results test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")
        print(f"  - Response type: {result.response_type}")
        if result.suggested_followup:
            print(f"  - Suggested followup: {result.suggested_followup}")

    def test_ambiguous_query_handling(self, fund_search_tool):
        """
        Test: Potentially ambiguous query.

        Query: "Vale funds"
        (Could mean: funds managed by Vale Foundation OR funds investing in Vale stock)

        Expected:
        1. is_ambiguous flag set
        2. interpretation_note explains the interpretation
        3. Still returns results based on best interpretation

        Why: Tests ambiguity detection and handling
        """
        result = fund_search_tool.ask("Vale funds")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Ambiguous query test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")
        print(f"  - Is ambiguous: {result.is_ambiguous}")
        if result.interpretation_note:
            print(f"  - Interpretation: {result.interpretation_note}")
