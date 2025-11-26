"""
Unit tests for SnapshotSearchTool.

Tests searching funds by snapshot metrics (AUM, holder count).
"""

import pytest

from src.agent.fund_search.models.query import NumericFilter
from src.agent.fund_search.tools.search_snapshots.tool import SnapshotSearchTool


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
            value=100000000,  # 100M
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
            value=100000000,  # 100M
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with AUM <= 100M
        assert len(results) == 2
        assert "11.222.333/0001-44" in results  # 50M
        assert "22.333.444/0001-55" in results  # 500k

    def test_search_by_min_holders(self, test_db_with_snapshots):
        """Test searching funds with minimum holder count."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="holders", operator="min", value=2000)

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with holders >= 2000
        assert len(results) == 2
        assert "12.345.678/0001-90" in results  # 5000
        assert "98.765.432/0001-10" in results  # 3000

    def test_search_by_max_holders(self, test_db_with_snapshots):
        """Test searching funds with maximum holder count."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="holders", operator="max", value=1000)

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with holders <= 1000
        assert len(results) == 1
        assert "22.333.444/0001-55" in results  # 50

    def test_search_results_ordered_descending(self, test_db_with_snapshots):
        """Test that results are ordered by metric value (descending)."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        # Should be ordered by AUM descending
        assert results[0] == "98.765.432/0001-10"  # Largest AUM
        assert results[-1] == "22.333.444/0001-55"  # Smallest AUM

    def test_search_with_cnpj_filter(self, test_db_with_snapshots):
        """Test searching with CNPJ filter."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)
        cnpjs = ["12.345.678/0001-90", "11.222.333/0001-44"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        # Should only return specified funds
        assert len(results) == 2
        assert set(results) == set(cnpjs)

    def test_search_with_limit(self, test_db_with_snapshots):
        """Test search respects limit parameter."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=2)

        assert len(results) == 2

    def test_search_no_results(self, test_db_with_snapshots):
        """Test search returns empty list when no matches."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=1000000000,  # 1B - too high
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
        numeric_filter = NumericFilter(metric="aum", operator="top", value=100000000)

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        # top operator should work like min (>=)
        assert len(results) == 2

    def test_search_with_zero_value(self, test_db_with_snapshots):
        """Test search with value=0 returns all funds."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        assert len(results) == 4  # All funds

    def test_search_with_none_value(self, test_db_with_snapshots):
        """Test search with value=None defaults to 0."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=None)

        results = tool.forward(numeric_filter=numeric_filter)

        # None should default to 0, returning all funds
        assert len(results) == 4

    def test_search_with_empty_cnpj_list(self, test_db_with_snapshots):
        """Test search with empty CNPJ list returns all matching funds."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=[])

        # Empty list should not filter, return all
        assert len(results) == 4

    def test_search_with_nonexistent_cnpj(self, test_db_with_snapshots):
        """Test search with non-existent CNPJ returns empty."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)
        cnpjs = ["99.999.999/0001-99"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        assert results == []

    def test_search_with_single_cnpj(self, test_db_with_snapshots):
        """Test search with single CNPJ filter."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)
        cnpjs = ["12.345.678/0001-90"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        assert len(results) == 1
        assert results[0] == "12.345.678/0001-90"

    def test_latest_snapshot_is_used(self, test_db_with_snapshots):
        """Test that only the latest snapshot for each fund is used."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        # FUND001 has two snapshots: 100M (older) and 150M (latest)
        # Searching for AUM >= 150M should return FUND001
        numeric_filter = NumericFilter(metric="aum", operator="min", value=150000000)

        results = tool.forward(numeric_filter=numeric_filter)

        # Should find FUND001 (150M) and FUND002 (250M)
        assert len(results) == 2
        assert "12.345.678/0001-90" in results
        assert "98.765.432/0001-10" in results

    def test_older_snapshot_not_used(self, test_db_with_snapshots):
        """Test that older snapshots are ignored."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        # FUND001 has older snapshot with 100M, but latest is 150M
        # Searching for AUM between 100M and 149M should NOT return FUND001
        numeric_filter = NumericFilter(metric="aum", operator="min", value=100000000)

        results = tool.forward(numeric_filter=numeric_filter)

        # Only FUND001 (150M) and FUND002 (250M) have >= 100M in latest snapshot
        assert len(results) == 2  # FUND001 (150M), FUND002 (250M)

    def test_holders_ordering(self, test_db_with_snapshots):
        """Test results ordered by holders descending."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="holders", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        # Should be ordered by holders descending: 5000, 3000, 1200, 50
        assert results[0] == "12.345.678/0001-90"  # 5000
        assert results[1] == "98.765.432/0001-10"  # 3000
        assert results[2] == "11.222.333/0001-44"  # 1200
        assert results[3] == "22.333.444/0001-55"  # 50

    def test_limit_zero(self, test_db_with_snapshots):
        """Test limit=0 returns empty list."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=0)

        assert results == []

    def test_limit_exceeds_results(self, test_db_with_snapshots):
        """Test limit larger than available results."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=100)

        # Only 4 funds, limit doesn't matter
        assert len(results) == 4

    def test_exact_threshold_match_min(self, test_db_with_snapshots):
        """Test min operator with exact value match."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=150000000,  # Exact match with FUND001
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should include exact match (>= includes equal)
        assert len(results) == 2
        assert "12.345.678/0001-90" in results

    def test_exact_threshold_match_max(self, test_db_with_snapshots):
        """Test max operator with exact value match."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="max",
            value=50000000,  # Exact match with FUND003
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should include exact match (<= includes equal)
        assert len(results) == 2
        assert "11.222.333/0001-44" in results

    def test_very_large_threshold(self, test_db_with_snapshots):
        """Test with threshold larger than any fund."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=1000000000000,  # 1 trillion
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_very_small_threshold_max(self, test_db_with_snapshots):
        """Test max with threshold smaller than any fund."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="max",
            value=1,  # 1 BRL
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_cnpj_filter_with_no_matching_metrics(self, test_db_with_snapshots):
        """Test CNPJ filter combined with impossible metric filter."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=1000000000,  # Too high for FUND001
        )
        cnpjs = ["12.345.678/0001-90"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        # FUND001 has only 150M, doesn't meet threshold
        assert results == []

    def test_multiple_cnpj_filter(self, test_db_with_snapshots):
        """Test filtering with multiple CNPJs."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)
        cnpjs = ["12.345.678/0001-90", "98.765.432/0001-10", "11.222.333/0001-44"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        assert len(results) == 3
        assert set(results) == set(cnpjs)

    def test_returns_list_of_strings(self, test_db_with_snapshots):
        """Test that results are list of CNPJ strings."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=1)

        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], str)
        assert "." in results[0]  # CNPJ format check

    def test_no_duplicate_cnpjs(self, test_db_with_snapshots):
        """Test that DISTINCT ensures no duplicate CNPJs in results."""
        tool = SnapshotSearchTool(db_path=test_db_with_snapshots)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        # All CNPJs should be unique
        assert len(results) == len(set(results))
