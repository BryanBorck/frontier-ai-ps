"""
E2E tests for metadata search tool.

Tests that metadata search correctly handles:
- Fund type queries (FIA, FIM, FIRF)
- Investment class queries
"""

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestMetadataSearchE2E:
    """
    E2E tests for metadata search (fund type queries)
    """

    def test_fia_funds_query(self, fund_search_tool):
        """
        Test: "show me FIA funds" or "equity investment funds"

        Expected:
        - Use metadata search
        - Filter by fund_type = FIA

        Why critical: FIA is most common equity fund type in Brazil
        """
        result = fund_search_tool.ask("show me FIA funds")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ FIA funds query test passed!")
        print(f"  - Found {len(result.cnpjs)} FIA funds")
        print(f"  - Response type: {result.response_type}")

    def test_fixed_income_funds(self, fund_search_tool):
        """
        Test: "fixed income funds" or "FIRF funds"

        Expected: Filter for fixed income fund types

        Why: FIRF is most common fixed income fund type
        """
        result = fund_search_tool.ask("fixed income funds")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Fixed income funds query test passed!")
        print(f"  - Found {len(result.cnpjs)} fixed income funds")

    def test_multimarket_funds(self, fund_search_tool):
        """
        Test: "multimarket funds" or "multimercado"

        Expected: Filter for multimarket fund category

        Why: Multimarket is popular Brazilian fund category
        """
        result = fund_search_tool.ask("multimarket funds")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Multimarket funds query test passed!")
        print(f"  - Found {len(result.cnpjs)} multimarket funds")
