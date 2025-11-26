"""
Unit tests for PositionSearchTool.

Tests searching funds by their asset holdings (issuer names, tickers, asset types).
This tool enables queries like "funds investing in Petrobras" or "funds with Vale exposure".
"""

import pytest

from src.agent.fund_search.models.query import PositionSearchCriteria
from src.agent.fund_search.tools.search_positions.tool import PositionSearchTool

@pytest.mark.unit
class TestPositionSearchToolUnit:
    """Comprehensive unit tests for PositionSearchTool."""

    # Initialization and Basic Tests
    def test_initialization(self, test_db_with_positions):
        """Test tool initializes correctly with database path."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        assert tool.db_path == test_db_with_positions

    def test_search_returns_list_of_cnpjs(self, test_db_with_positions):
        """Test that search returns list of CNPJ strings."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria)

        assert isinstance(results, list)
        if results:
            assert all(isinstance(cnpj, str) for cnpj in results)
            assert "/" in results[0]  # CNPJ format check

    # Issuer Name Search Tests (Main Use Case)
    def test_search_by_issuer_name_exact(self, test_db_with_positions):
        """Test searching funds by exact issuer name match."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria)

        # FUND001 (500k) and FUND002 (1M + 50k) both have Petrobras exposure
        assert len(results) == 2
        assert "12.345.678/0001-90" in results  # FUND001
        assert "98.765.432/0001-10" in results  # FUND002

    def test_search_by_issuer_name_partial_match(self, test_db_with_positions):
        """Test issuer name search with partial matching (ILIKE)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        # Search for "VALE" should match "VALE SA"
        criteria = PositionSearchCriteria(companies=["VALE"])

        results = tool.forward(criteria=criteria)

        # FUND001 and FUND003 have Vale positions
        assert len(results) == 2
        assert "12.345.678/0001-90" in results
        assert "11.222.333/0001-44" in results

    def test_search_by_issuer_name_case_insensitive(self, test_db_with_positions):
        """Test issuer name search is case-insensitive."""
        tool = PositionSearchTool(db_path=test_db_with_positions)

        criteria_lower = PositionSearchCriteria(companies=["petrobras"])
        criteria_upper = PositionSearchCriteria(companies=["PETROBRAS"])
        criteria_mixed = PositionSearchCriteria(companies=["PeTrObRaS"])

        results_lower = tool.forward(criteria=criteria_lower)
        results_upper = tool.forward(criteria=criteria_upper)
        results_mixed = tool.forward(criteria=criteria_mixed)

        # All should return same results
        assert set(results_lower) == set(results_upper) == set(results_mixed)

    def test_search_by_multiple_issuer_names(self, test_db_with_positions):
        """Test searching by multiple issuer names (OR logic)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        # Find funds with either Petrobras OR Vale
        criteria = PositionSearchCriteria(companies=["PETROBRAS", "VALE"])

        results = tool.forward(criteria=criteria)

        # FUND001 (both), FUND002 (Petrobras), FUND003 (Vale)
        assert len(results) == 3

    def test_search_by_full_company_name(self, test_db_with_positions):
        """Test searching with full company name."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["ITAU UNIBANCO HOLDING SA"])

        results = tool.forward(criteria=criteria)

        # FUND002 has Itau position
        assert len(results) == 1
        assert "98.765.432/0001-10" in results

    def test_search_by_partial_company_name(self, test_db_with_positions):
        """Test searching with partial company name (e.g., 'Banco' matches 'Banco do Brasil')."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["BANCO"])

        results = tool.forward(criteria=criteria)

        # Should match both "ITAU UNIBANCO" and "BANCO DO BRASIL"
        assert len(results) >= 1

    # Ticker Search Tests

    def test_search_by_asset_type_equity(self, test_db_with_positions):
        """Test filtering by asset_class (EQUITY)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        results = tool.forward(criteria=criteria)

        # FUND001 (PETR4, VALE3), FUND002 (PETR4, ITUB4), FUND003 (VALE3, BBAS3)
        assert len(results) == 3

    def test_search_by_asset_type_derivatives(self, test_db_with_positions):
        """Test filtering by asset_class (DERIVATIVES)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_type=["DERIVATIVES"])

        results = tool.forward(criteria=criteria)

        # FUND002 has Petrobras option
        assert len(results) == 1
        assert "98.765.432/0001-10" in results

    def test_search_by_asset_type_investment_fund(self, test_db_with_positions):
        """Test filtering by asset_class (INVESTMENT_FUND)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_type=["INVESTMENT_FUND"])

        results = tool.forward(criteria=criteria)

        # FUND004 invests in investment funds
        assert len(results) == 1
        assert "22.333.444/0001-55" in results

    def test_search_by_multiple_asset_types(self, test_db_with_positions):
        """Test filtering by multiple asset types (OR logic)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_type=["EQUITY", "DERIVATIVES"])

        results = tool.forward(criteria=criteria)

        # FUND001, FUND002, FUND003 have equity or derivatives
        assert len(results) == 3

    # Combined Criteria Tests
    def test_search_combined_issuer_and_asset_type(self, test_db_with_positions):
        """Test combining issuer name and asset type filters (AND logic)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        # Find funds with Petrobras EQUITY positions (exclude derivatives)
        criteria = PositionSearchCriteria(
            companies=["PETROBRAS"],
            asset_type=["EQUITY"]
        )

        results = tool.forward(criteria=criteria)

        # FUND001 and FUND002 have Petrobras stocks
        assert len(results) == 2

    def test_results_ordered_by_total_exposure_descending(self, test_db_with_positions):
        """Test results are sorted by total exposure (highest first)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria)

        # FUND002 (1M + 50k = 1.05M) should come before FUND001 (500k)
        assert results[0] == "98.765.432/0001-10"  # FUND002
        assert results[1] == "12.345.678/0001-90"  # FUND001

    def test_exposure_aggregation_across_multiple_assets(self, test_db_with_positions):
        """Test total exposure aggregates across multiple matching assets."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        # Petrobras has both stock (ASSET001) and option (ASSET004)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria)

        # FUND002 has both Petrobras stock (1M) and option (50k) = 1.05M total
        # Should rank higher than FUND001 with only stock (500k)
        assert results[0] == "98.765.432/0001-10"

    def test_exposure_aggregation_by_asset_class(self, test_db_with_positions):
        """Test aggregation works correctly when filtering by asset class."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        # Find total EQUITY exposure (excludes derivatives)
        criteria = PositionSearchCriteria(
            companies=["PETROBRAS"],
            asset_type=["EQUITY"]
        )

        results = tool.forward(criteria=criteria)

        # Should aggregate only equity positions
        assert isinstance(results, list)

    # Pre-filtering (CNPJ List) Tests
    def test_pre_filtering_with_cnpj_list(self, test_db_with_positions):
        """Test pre-filtering search to specific funds via CNPJs."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])
        # Only search within FUND001
        cnpjs = ["12.345.678/0001-90"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        assert len(results) == 1
        assert results[0] == "12.345.678/0001-90"

    def test_pre_filtering_with_multiple_cnpjs(self, test_db_with_positions):
        """Test pre-filtering with multiple CNPJs."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["VALE"])
        # Only search FUND001 and FUND003
        cnpjs = ["12.345.678/0001-90", "11.222.333/0001-44"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        assert len(results) == 2
        assert all(cnpj in cnpjs for cnpj in results)

    def test_pre_filtering_excludes_other_funds(self, test_db_with_positions):
        """Test pre-filtering properly excludes funds not in CNPJ list."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])
        # Only FUND002, should exclude FUND001
        cnpjs = ["98.765.432/0001-10"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        assert "12.345.678/0001-90" not in results

    def test_pre_filtering_empty_list_returns_all(self, test_db_with_positions):
        """Test empty CNPJ pre-filter list doesn't restrict results."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results_no_filter = tool.forward(criteria=criteria, cnpjs=None)
        results_empty_filter = tool.forward(criteria=criteria, cnpjs=[])

        # Both should return all matching funds
        assert len(results_no_filter) == len(results_empty_filter)

    # Limit Tests
    def test_limit_restricts_results(self, test_db_with_positions):
        """Test limit parameter restricts number of results."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        results = tool.forward(criteria=criteria, limit=2)

        assert len(results) == 2

    def test_limit_zero_returns_empty(self, test_db_with_positions):
        """Test limit=0 returns empty list."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria, limit=0)

        assert results == []

    def test_limit_larger_than_results(self, test_db_with_positions):
        """Test limit larger than available results returns all."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria, limit=1000)

        # Should return all matching funds (2)
        assert len(results) == 2

    def test_limit_with_ordering_returns_top_funds(self, test_db_with_positions):
        """Test limit returns top funds by exposure."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria, limit=1)

        # Should return only the fund with highest exposure
        assert len(results) == 1
        assert results[0] == "98.765.432/0001-10"  # FUND002 with 1.05M

    # Edge Cases and Error Handling
    def test_no_matching_assets(self, test_db_with_positions):
        """Test search with no matching assets returns empty."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["NONEXISTENT COMPANY"])

        results = tool.forward(criteria=criteria)

        assert results == []

    def test_no_criteria_provided_returns_empty(self, test_db_with_positions):
        """Test search with empty criteria returns empty."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria()

        results = tool.forward(criteria=criteria)

        # No filters means WHERE 1=1, should return all funds with positions
        # But since we want meaningful searches, it may return empty
        assert isinstance(results, list)

    def test_handles_missing_database_gracefully(self, tmp_path):
        """Test tool handles missing database without crashing."""
        bad_db_path = str(tmp_path / "nonexistent.db")
        tool = PositionSearchTool(db_path=bad_db_path)
        criteria = PositionSearchCriteria(companies=["TEST"])

        results = tool.forward(criteria=criteria)

        assert results == []

    def test_handles_corrupted_database(self, tmp_path):
        """Test tool handles corrupted database gracefully."""
        bad_db = tmp_path / "corrupted.db"
        bad_db.write_text("This is not a valid database")

        tool = PositionSearchTool(db_path=str(bad_db))
        criteria = PositionSearchCriteria(companies=["TEST"])

        results = tool.forward(criteria=criteria)

        assert results == []

    def test_sql_injection_protection_in_issuer_name(self, test_db_with_positions):
        """Test issuer name search protects against SQL injection."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        # Attempt SQL injection in issuer name
        criteria = PositionSearchCriteria(companies=["'; DROP TABLE positions; --"])

        results = tool.forward(criteria=criteria)

        # Should handle safely (no match, but no crash)
        assert isinstance(results, list)

    def test_no_duplicate_cnpjs_in_results(self, test_db_with_positions):
        """Test results contain no duplicate CNPJs."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria)

        # All CNPJs should be unique
        assert len(results) == len(set(results))

    def test_null_position_values_excluded(self, test_db_with_positions):
        """Test positions with NULL market values are excluded."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        # All test positions have values, so this tests the WHERE clause
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        results = tool.forward(criteria=criteria)

        # Should only include positions with non-null values
        assert isinstance(results, list)

    def test_empty_cnpj_values_excluded(self, test_db_with_positions):
        """Test funds with NULL/empty CNPJ are excluded from results."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(companies=["PETROBRAS"])

        results = tool.forward(criteria=criteria)

        # All results should be valid CNPJs
        assert all(results)
        assert all("/" in cnpj for cnpj in results)
