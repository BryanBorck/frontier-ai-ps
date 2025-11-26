"""
Unit tests for PositionSearchTool.

Tests searching funds by their asset positions/holdings.
"""

import pytest
from src.agent.fund_search.tools.search_positions.tool import PositionSearchTool
from src.agent.fund_search.models.query import PositionSearchCriteria


@pytest.mark.unit
class TestPositionSearchTool:
    """Unit tests for PositionSearchTool."""

    def test_initialization(self, test_db_with_positions):
        """Test tool initializes correctly."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        assert tool.db_path == test_db_with_positions

    def test_search_by_asset_name(self, test_db_with_positions):
        """Test searching funds by asset name."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_name=["Petrobras PN"])

        results = tool.forward(criteria=criteria)

        # Should return funds holding Petrobras, ordered by exposure
        assert len(results) == 2
        assert "98.765.432/0001-10" in results  # Largest exposure
        assert "12.345.678/0001-90" in results

    def test_search_by_ticker(self, test_db_with_positions):
        """Test searching funds by ticker."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_tickers=["VALE3"])

        results = tool.forward(criteria=criteria)

        assert len(results) == 2
        assert "12.345.678/0001-90" in results
        assert "11.222.333/0001-44" in results

    def test_search_by_asset_type(self, test_db_with_positions):
        """Test searching funds by asset type."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_type=["Equity"])

        results = tool.forward(criteria=criteria)

        # All test positions are equity
        assert len(results) == 3

    def test_search_with_cnpj_filter(self, test_db_with_positions):
        """Test searching positions within specific funds."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_name=["Petrobras PN"])
        cnpjs = ["12.345.678/0001-90"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        # Should only return the filtered fund
        assert len(results) == 1
        assert results[0] == "12.345.678/0001-90"

    def test_search_results_ordered_by_exposure(self, test_db_with_positions):
        """Test that results are ordered by total exposure (descending)."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_name=["Petrobras PN"])

        results = tool.forward(criteria=criteria)

        # Fund with larger Petrobras exposure should come first
        assert results[0] == "98.765.432/0001-10"  # 1M exposure
        assert results[1] == "12.345.678/0001-90"  # 500k exposure

    def test_search_with_limit(self, test_db_with_positions):
        """Test search respects limit parameter."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_type=["Equity"])

        results = tool.forward(criteria=criteria, limit=2)

        assert len(results) == 2

    def test_search_no_results(self, test_db_with_positions):
        """Test search returns empty list when no matches."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(asset_name=["NONEXISTENT ASSET"])

        results = tool.forward(criteria=criteria)

        assert results == []

    def test_search_multiple_criteria(self, test_db_with_positions):
        """Test searching with multiple criteria combined."""
        tool = PositionSearchTool(db_path=test_db_with_positions)
        criteria = PositionSearchCriteria(
            asset_type=["Equity"],
            asset_tickers=["PETR4"]
        )

        results = tool.forward(criteria=criteria)

        assert len(results) == 2

    def test_search_error_handling(self, tmp_path):
        """Test tool handles database errors gracefully."""
        bad_db_path = str(tmp_path / "nonexistent.db")
        tool = PositionSearchTool(db_path=bad_db_path)
        criteria = PositionSearchCriteria(asset_name=["Test"])

        # Should return empty list instead of crashing
        results = tool.forward(criteria=criteria)

        assert results == []