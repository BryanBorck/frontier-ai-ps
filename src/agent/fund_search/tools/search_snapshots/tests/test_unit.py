"""
Unit tests for SnapshotSearchTool.

Tests searching funds by snapshot metrics (AUM, holder count).
"""

import pytest
from src.agent.fund_search.tools.search_snapshots.tool import SnapshotSearchTool
from src.agent.fund_search.models.query import NumericFilter


@pytest.mark.unit
class TestSnapshotSearchTool:
    """Unit tests for SnapshotSearchTool."""

    def test_initialization(self, test_db_with_snapshots):
        """Test tool initializes correctly."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        assert tool.db_path == test_db_with_snapshots

    def test_search_by_min_aum(self, test_db_with_snapshots):
        """Test searching funds with minimum AUM."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=100000000  # 100M
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with AUM >= 100M
        assert len(results) == 2
        assert "12.345.678/0001-90" in results  # 150M
        assert "98.765.432/0001-10" in results  # 250M

    def test_search_by_max_aum(self, test_db_with_snapshots):
        """Test searching funds with maximum AUM."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="max",
            value=100000000  # 100M
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with AUM <= 100M
        assert len(results) == 2
        assert "11.222.333/0001-44" in results  # 50M
        assert "22.333.444/0001-55" in results  # 500k

    def test_search_by_min_holders(self, test_db_with_snapshots):
        """Test searching funds with minimum holder count."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="holders",
            operator="min",
            value=2000
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with holders >= 2000
        assert len(results) == 2
        assert "12.345.678/0001-90" in results  # 5000
        assert "98.765.432/0001-10" in results  # 3000

    def test_search_by_max_holders(self, test_db_with_snapshots):
        """Test searching funds with maximum holder count."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="holders",
            operator="max",
            value=1000
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with holders <= 1000
        assert len(results) == 1
        assert "22.333.444/0001-55" in results  # 50

    def test_search_results_ordered_descending(self, test_db_with_snapshots):
        """Test that results are ordered by metric value (descending)."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=0
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should be ordered by AUM descending
        assert results[0] == "98.765.432/0001-10"  # Largest AUM
        assert results[-1] == "22.333.444/0001-55"  # Smallest AUM

    def test_search_with_cnpj_filter(self, test_db_with_snapshots):
        """Test searching with CNPJ filter."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=0
        )
        cnpjs = ["12.345.678/0001-90", "11.222.333/0001-44"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        # Should only return specified funds
        assert len(results) == 2
        assert set(results) == set(cnpjs)

    def test_search_with_limit(self, test_db_with_snapshots):
        """Test search respects limit parameter."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=0
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=2)

        assert len(results) == 2

    def test_search_no_results(self, test_db_with_snapshots):
        """Test search returns empty list when no matches."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=1000000000  # 1B - too high
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_search_error_handling(self, tmp_path):
        """Test tool handles database errors gracefully."""
        bad_db_path = str(tmp_path / "nonexistent.db")
        tool = SnapshotSearchTool(db_path=bad_db_path)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        # Should return empty list instead of crashing
        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_search_top_operator(self, test_db_with_snapshots):
        """Test search with 'top' operator (same as min)."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="top",
            value=100000000
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        # top operator should work like min (>=)
        assert len(results) == 2
