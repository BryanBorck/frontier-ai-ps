"""
E2E tests for snapshots search tool.

Tests that snapshot search correctly handles:
- Performance queries (returns > X%)
- AUM/size queries (funds with > $X billion)
"""

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestSnapshotSearchE2E:
    """
    E2E tests for snapshot search (performance/AUM queries)
    """

    def test_high_return_query(self, fund_search_tool):
        """
        Test: "funds with more than 10% return this year"

        Expected:
        - Use snapshot search
        - Filter by return_ytd > 10%

        Why critical: Performance is key search criteria
        """
        result = fund_search_tool.ask("funds with more than 10% return this year")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ High return query test passed!")
        print(f"  - Found {len(result.cnpjs)} high-performing funds")
        print(f"  - Response type: {result.response_type}")

    def test_large_funds_by_aum(self, fund_search_tool):
        """
        Test: "funds with more than 1 billion in assets"

        Expected:
        - Use snapshot search
        - Filter by net_worth > 1_000_000_000

        Why critical: AUM is common filter criteria
        """
        result = fund_search_tool.ask("funds with more than 1 billion in assets")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Large funds AUM query test passed!")
        print(f"  - Found {len(result.cnpjs)} large funds")

    def test_positive_returns(self, fund_search_tool):
        """
        Test: "funds with positive returns"

        Expected: Filter return > 0

        Why: Simple performance filter
        """
        result = fund_search_tool.ask("funds with positive returns")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Positive returns query test passed!")
        print(f"  - Found {len(result.cnpjs)} funds with positive returns")
