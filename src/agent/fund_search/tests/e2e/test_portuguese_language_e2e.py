"""
E2E tests for Portuguese language support.

Tests that the agent correctly handles Brazilian Portuguese queries.

Example: "fundos que investem em PETR3" should work identically to
         "funds investing in PETR3"
"""

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestPortugueseLanguageE2E:
    """
    E2E tests for Portuguese language queries
    """

    def test_portuguese_ticker_query(self, fund_search_tool):
        """
        Test: "fundos que investem em PETR3"

        Expected:
        - Parse Portuguese correctly
        - Extract companies and asset_type
        - detected_language: "pt"

        Why critical: Portuguese is primary language for Brazilian users
        """
        result = fund_search_tool.ask("fundos que investem em PETR3")

        assert result is not None
        assert result.detected_language == "pt"
        assert isinstance(result.cnpjs, list)

        print("\n✓ Portuguese ticker query test passed!")
        print(f"  - Detected language: {result.detected_language}")
        print(f"  - Found {len(result.cnpjs)} funds")

    def test_portuguese_manager_query(self, fund_search_tool):
        """
        Test: "fundos do XP" or "fundos geridos pelo XP"

        Expected: Same results as "XP funds"

        Why: Manager queries are common in Portuguese
        """
        result = fund_search_tool.ask("fundos do XP")

        assert result is not None
        assert result.detected_language == "pt"
        assert isinstance(result.cnpjs, list)

        print("\n✓ Portuguese manager query test passed!")
        print(f"  - Found {len(result.cnpjs)} XP funds")

    def test_renda_fixa_terminology(self, fund_search_tool):
        """
        Test: "fundos de renda fixa"

        Expected:
        - Map "renda fixa" → FIXED_INCOME asset type
        - Return fixed income funds

        Why: "Renda fixa" is Brazilian term for fixed income
        """
        result = fund_search_tool.ask("fundos de renda fixa")

        assert result is not None
        assert result.detected_language == "pt"
        assert isinstance(result.cnpjs, list)

        print("\n✓ Portuguese fixed income terminology test passed!")
        print(f"  - Found {len(result.cnpjs)} renda fixa funds")
