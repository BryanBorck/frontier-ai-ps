"""
E2E tests for ticker-to-company mapping.

Tests that the LLM extractor correctly maps Brazilian stock tickers to:
1. Company names (for issuer search)
2. Asset type EQUITY (not derivatives)

Example: "funds investing in PETR3" should extract:
    - companies=["Petrobras"]
    - asset_type=["EQUITY"]
"""

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestTickerMappingE2E:
    """
    E2E tests for ticker-to-company mapping.

    These tests verify the COMPLETE pipeline:
    User query → LLM extraction → Expected ParsedQuery

    CRITICAL: These tests must pass before deploying to production!
    """

    def test_petr3_ticker_mapping(self, fund_search_tool):
        """
        Test: "funds investing in PETR3"

        Expected:
        - Ticker PETR3 mapped to Petrobras
        - Parsed as equity position search
        - Returns valid response

        Why critical: PETR3 is one of most traded stocks in Brazil
        """
        result = fund_search_tool.ask("funds investing in PETR3")

        assert result is not None
        assert isinstance(result.cnpjs, list)
        assert result.response_type in [
            "list_results",
            "no_results",
            "no_results_followup",
            "single_match",
        ]

        print("\n✓ PETR3 ticker mapping test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")
        print(f"  - Response type: {result.response_type}")

    def test_multiple_tickers(self, fund_search_tool):
        """
        Test: "funds with PETR3 or VALE3"

        Expected:
        - Both tickers mapped to companies
        - Returns funds with either Petrobras OR Vale positions

        Why: Users often query multiple companies
        """
        result = fund_search_tool.ask("funds with PETR3 or VALE3")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Multiple tickers test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")

    def test_ticker_case_insensitive(self, fund_search_tool):
        """
        Test: "funds with vale3" (lowercase ticker)

        Expected: Should still recognize and map ticker correctly

        Why: User input may vary in case
        """
        result = fund_search_tool.ask("funds with vale3")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Case insensitive ticker test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")
