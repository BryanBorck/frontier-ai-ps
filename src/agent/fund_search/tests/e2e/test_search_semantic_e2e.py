"""
E2E tests for semantic search tool.

Tests that semantic search correctly handles:
- Manager/institution queries (XP, BTG, Itaú)
- Investment strategy queries (small cap, ESG)
"""

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestSemanticSearchE2E:
    """
    E2E tests for semantic search (manager/strategy queries)
    """

    def test_manager_query_xp(self, fund_search_tool):
        """
        Test: "funds managed by XP"

        Expected:
        - Use semantic search (not position search)
        - Return funds with XP as manager/administrator

        Why critical: Users often search by manager name
        """
        result = fund_search_tool.ask("funds managed by XP")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ XP manager query test passed!")
        print(f"  - Found {len(result.cnpjs)} XP funds")
        print(f"  - Response type: {result.response_type}")

    def test_strategy_query_small_cap(self, fund_search_tool):
        """
        Test: "funds with small cap strategy"

        Expected:
        - Use semantic search
        - Find funds with small cap in strategy description

        Why critical: Strategy-based search is key use case
        """
        result = fund_search_tool.ask("funds with small cap strategy")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Small cap strategy query test passed!")
        print(f"  - Found {len(result.cnpjs)} small cap funds")

    def test_manager_btg(self, fund_search_tool):
        """
        Test: "show me BTG funds"

        Expected: Similar to XP query, should find BTG-managed funds

        Why: BTG is another major Brazilian fund manager
        """
        result = fund_search_tool.ask("show me BTG funds")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ BTG manager query test passed!")
        print(f"  - Found {len(result.cnpjs)} BTG funds")
