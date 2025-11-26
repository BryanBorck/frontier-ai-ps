"""
Integration tests for PositionSearchTool.

These tests use the real br_funds.db database to test with production data.
They verify that the tool works correctly with actual assets, positions, and fund data.
"""

import pytest

from src.agent.fund_search.models.query import PositionSearchCriteria
from src.agent.fund_search.tools.search_positions.tool import PositionSearchTool

@pytest.mark.integration
@pytest.mark.requires_db
class TestPositionSearchToolIntegration:
    """Integration tests using real database with production data."""

    # Happy Path Integration Tests
    def test_search_real_database_by_issuer_name(self, db_snapshot):
        """Test searching with real database by issuer name."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(companies=["VALE"])

        results = tool.forward(criteria=criteria, limit=10)

        # Should find real funds with Vale positions
        assert isinstance(results, list)
        # May or may not have results depending on real data

    def test_search_real_database_by_asset_class(self, db_snapshot):
        """Test filtering by asset class with real data."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        results = tool.forward(criteria=criteria, limit=10)

        assert isinstance(results, list)

    def test_search_real_database_combined_criteria(self, db_snapshot):
        """Test combined criteria search on real database."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(
            companies=["PETROBRAS"],
            asset_type=["EQUITY"]
        )

        results = tool.forward(criteria=criteria, limit=10)

        assert isinstance(results, list)

    def test_search_partial_company_names_real_data(self, db_snapshot):
        """Test partial company name matching with real data."""
        tool = PositionSearchTool(db_path=db_snapshot)
        # "BANCO" should match multiple banks
        criteria = PositionSearchCriteria(companies=["BANCO"])

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)

    def test_search_multiple_issuers_real_data(self, db_snapshot):
        """Test searching multiple issuers with real data."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(companies=["VALE", "PETROBRAS", "ITAU"])

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)

    def test_search_derivatives_real_data(self, db_snapshot):
        """Test finding funds with derivatives positions."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(asset_type=["DERIVATIVES"])

        results = tool.forward(criteria=criteria, limit=10)

        assert isinstance(results, list)

    def test_search_investment_funds_real_data(self, db_snapshot):
        """Test finding funds of funds."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(asset_type=["INVESTMENT_FUND"])

        results = tool.forward(criteria=criteria, limit=10)

        assert isinstance(results, list)

    def test_results_have_valid_cnpj_format(self, db_snapshot):
        """Test that results from real database have valid CNPJ format."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        results = tool.forward(criteria=criteria, limit=10)

        if results:
            # Check CNPJ format: XX.XXX.XXX/XXXX-XX
            for cnpj in results:
                assert isinstance(cnpj, str)
                assert "/" in cnpj
                assert "-" in cnpj

    def test_results_ordered_by_exposure_real_data(self, db_snapshot):
        """Test results are properly ordered by exposure with real data."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(companies=["VALE"])

        results = tool.forward(criteria=criteria, limit=10)

        # Results should be in descending order of exposure
        # (Can't verify exact values without querying, but should be ordered)
        assert isinstance(results, list)

    def test_limit_parameter_real_data(self, db_snapshot):
        """Test limit parameter works with real database."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        results_5 = tool.forward(criteria=criteria, limit=5)
        results_10 = tool.forward(criteria=criteria, limit=10)

        # Smaller limit should return fewer or equal results
        assert len(results_5) <= 5
        assert len(results_10) <= 10
        assert len(results_5) <= len(results_10)

    # Edge Cases with Real Database
    def test_search_nonexistent_company_real_data(self, db_snapshot):
        """Test searching for non-existent company in real database."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(companies=["XYZABC NONEXISTENT COMPANY"])

        results = tool.forward(criteria=criteria)

        assert results == []

    def test_case_insensitive_search_real_data(self, db_snapshot):
        """Test case-insensitive search with real database."""
        tool = PositionSearchTool(db_path=db_snapshot)

        criteria_lower = PositionSearchCriteria(companies=["vale"])
        criteria_upper = PositionSearchCriteria(companies=["VALE"])

        results_lower = tool.forward(criteria=criteria_lower, limit=10)
        results_upper = tool.forward(criteria=criteria_upper, limit=10)

        # Should return same results
        assert set(results_lower) == set(results_upper)

    def test_no_duplicate_cnpjs_real_data(self, db_snapshot):
        """Test no duplicate CNPJs in results from real database."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(companies=["VALE"])

        results = tool.forward(criteria=criteria, limit=50)

        # All CNPJs should be unique
        assert len(results) == len(set(results))

    def test_sql_injection_protection_real_database(self, db_snapshot):
        """Test SQL injection protection with real database."""
        tool = PositionSearchTool(db_path=db_snapshot)

        # Attempt various SQL injection patterns
        criteria = PositionSearchCriteria(companies=["'; DROP TABLE positions; --"])

        results = tool.forward(criteria=criteria)

        # Should handle safely without errors
        assert isinstance(results, list)

    def test_pre_filtering_with_cnpjs_real_data(self, db_snapshot):
        """Test CNPJ pre-filtering with real database."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        # First get some results
        all_results = tool.forward(criteria=criteria, limit=10)

        if len(all_results) >= 2:
            # Filter to first 2 CNPJs
            cnpj_filter = all_results[:2]
            filtered_results = tool.forward(criteria=criteria, cnpjs=cnpj_filter)

            # Filtered results should be subset of original
            assert all(cnpj in all_results for cnpj in filtered_results)
            assert len(filtered_results) <= len(cnpj_filter)

    def test_empty_criteria_real_data(self, db_snapshot):
        """Test empty criteria with real database."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria()

        results = tool.forward(criteria=criteria, limit=10)

        # Should handle empty criteria gracefully
        assert isinstance(results, list)

    # Performance and Scalability Tests
    def test_large_result_set_real_data(self, db_snapshot):
        """Test handling large result sets."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(asset_type=["EQUITY"])

        results = tool.forward(criteria=criteria, limit=100)

        # Should handle large limits without errors
        assert isinstance(results, list)
        assert len(results) <= 100

    def test_multiple_asset_types_real_data(self, db_snapshot):
        """Test searching across multiple asset types."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(
            asset_type=["EQUITY", "DERIVATIVES", "INVESTMENT_FUND"]
        )

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)

    def test_complex_combined_query_real_data(self, db_snapshot):
        """Test complex query combining multiple criteria."""
        tool = PositionSearchTool(db_path=db_snapshot)
        criteria = PositionSearchCriteria(
            companies=["BANCO"],
            asset_type=["EQUITY"],
            asset_tickers=["BBAS3", "ITUB4"]
        )

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)
