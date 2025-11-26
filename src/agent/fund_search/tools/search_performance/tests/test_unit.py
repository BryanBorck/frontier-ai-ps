"""
Unit tests for PerformanceSearchTool.

Tests searching funds by performance metrics (returns).
"""

import pytest
from src.agent.fund_search.tools.search_performance.tool import PerformanceSearchTool
from src.agent.fund_search.models.query import NumericFilter


@pytest.mark.unit
class TestPerformanceSearchTool:
    """Unit tests for PerformanceSearchTool."""

    def test_initialization(self, test_db_with_performance):
        """Test tool initializes correctly."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        assert tool.db_path == test_db_with_performance

    def test_search_by_min_return(self, test_db_with_performance):
        """Test searching funds with minimum return."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=20.0,  # 20% return
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with return > 20%
        assert isinstance(results, list)
        # Fund-1 has total return of 23.5% (15.5 + 8.0)
        assert "12.345.678/0001-90" in results

    def test_search_by_max_return(self, test_db_with_performance):
        """Test searching funds with maximum return."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="max",
            value=10.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with return < 10%
        assert isinstance(results, list)

    def test_search_with_cdi_benchmark(self, test_db_with_performance):
        """Test searching with CDI benchmark."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            benchmark_name="CDI",
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds outperforming CDI (10%)
        assert isinstance(results, list)

    def test_search_with_selic_benchmark(self, test_db_with_performance):
        """Test searching with SELIC benchmark."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            benchmark_name="SELIC",
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds outperforming SELIC (10.5%)
        assert isinstance(results, list)

    def test_search_with_ytd_period(self, test_db_with_performance):
        """Test searching with YTD performance period."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=5.0,
            performance_period="ytd"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert isinstance(results, list)

    def test_search_with_custom_period(self, test_db_with_performance):
        """Test searching with custom month period."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=10.0,
            performance_period="3m"  # 3 months
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert isinstance(results, list)

    def test_search_with_cnpj_filter(self, test_db_with_performance):
        """Test searching with CNPJ filter."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )
        cnpjs = ["12.345.678/0001-90"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        # Should only search within specified funds
        if results:  # Results depend on actual performance
            assert all(cnpj in cnpjs for cnpj in results)

    def test_search_with_limit(self, test_db_with_performance):
        """Test search respects limit parameter."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=1)

        assert len(results) <= 1

    def test_search_ignores_non_return_metrics(self, test_db_with_performance):
        """Test that non-return metrics are ignored."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="aum",  # Wrong metric
            operator="min",
            value=100.0
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return empty list for non-return metrics
        assert results == []

    def test_search_error_handling(self, tmp_path):
        """Test tool handles database errors gracefully."""
        bad_db_path = str(tmp_path / "nonexistent.db")
        tool = PerformanceSearchTool(db_path=bad_db_path)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=10.0
        )

        # Should return empty list instead of crashing
        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_search_results_ordered_by_return(self, test_db_with_performance):
        """Test that results are ordered by return (descending)."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should be ordered by total return descending
        if len(results) > 1:
            # Fund-1 should be first (highest return)
            assert results[0] == "12.345.678/0001-90"
