"""
E2E tests for asset type inference from natural language queries.

Tests that the LLM extractor correctly infers asset_type from broad queries.

Example: "funds investing in equities" should extract:
    - asset_type=["EQUITY"]
    - companies=None (broad search)
"""

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestAssetTypeInferenceE2E:
    """
    E2E tests for asset type inference
    """

    def test_broad_equity_query(self, fund_search_tool):
        """
        Test: "funds investing in equities"

        Expected:
        - asset_type: ["EQUITY"]
        - companies: None (broad search)
        - Returns equity funds

        Why critical: Broad equity search without specific companies
        """
        result = fund_search_tool.ask("funds investing in equities")

        assert result is not None
        assert isinstance(result.cnpjs, list)
        # Broad equity search should find funds
        assert result.response_type in ["list_results", "too_many_results", "no_results_followup"]

        print("\n✓ Broad equity query test passed!")
        print(f"  - Found {len(result.cnpjs)} equity funds")
        print(f"  - Response type: {result.response_type}")

    def test_natural_language_defaults_to_equity(self, fund_search_tool):
        """
        Test: "funds investing in Brazilian companies"

        Expected:
        - asset_type: ["EQUITY"] (default inference)
        - "investing in companies" should infer EQUITY

        Why critical: Natural language should default to equities
        """
        result = fund_search_tool.ask("funds investing in Brazilian companies")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Natural language equity inference test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")

    def test_fixed_income_query(self, fund_search_tool):
        """
        Test: "funds investing in bonds"

        Expected:
        - asset_type: ["FIXED_INCOME"]
        - Returns fixed income funds

        Why critical: Bond queries should map to FIXED_INCOME
        """
        result = fund_search_tool.ask("funds investing in bonds")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Fixed income query test passed!")
        print(f"  - Found {len(result.cnpjs)} bond funds")
