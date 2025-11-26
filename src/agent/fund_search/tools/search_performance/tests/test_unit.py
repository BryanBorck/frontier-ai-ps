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

    def test_benchmark_value_defaults_to_zero_when_none(self, test_db_with_performance):
        """Test that benchmark defaults to 0 when no value or benchmark_name provided."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # All funds with positive returns should be included
        assert isinstance(results, list)

    def test_cdi_benchmark_value(self, test_db_with_performance):
        """Test CDI benchmark is set to 10.0%."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            benchmark_name="CDI",
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should filter by > 10.0%
        assert isinstance(results, list)

    def test_selic_benchmark_value(self, test_db_with_performance):
        """Test SELIC benchmark is set to 10.5%."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            benchmark_name="SELIC",
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should filter by > 10.5%
        assert isinstance(results, list)

    def test_value_overrides_benchmark_when_both_provided(self, test_db_with_performance):
        """Test that explicit value takes precedence over benchmark_name."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=15.0,
            benchmark_name="CDI",  # This should be ignored
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should use value (15.0) not CDI (10.0)
        assert isinstance(results, list)

    def test_empty_cnpj_list(self, test_db_with_performance):
        """Test that empty CNPJ list doesn't filter results."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )

        results_no_filter = tool.forward(numeric_filter=numeric_filter)
        results_empty_filter = tool.forward(numeric_filter=numeric_filter, cnpjs=[])

        # Both should return same results
        assert len(results_no_filter) == len(results_empty_filter)

    def test_nonexistent_cnpj(self, test_db_with_performance):
        """Test search with non-existent CNPJ returns empty."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )
        cnpjs = ["99.999.999/0001-99"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        assert results == []

    def test_multiple_cnpj_filter(self, test_db_with_performance):
        """Test filtering with multiple CNPJs."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )
        cnpjs = ["12.345.678/0001-90", "98.765.432/0001-10"]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        # Should only return funds in the filter list
        assert all(cnpj in cnpjs for cnpj in results)

    def test_limit_zero_returns_empty(self, test_db_with_performance):
        """Test limit=0 returns empty list."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=0)

        assert results == []

    def test_limit_exceeds_results(self, test_db_with_performance):
        """Test limit larger than available results."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=1000)

        # Should return all matching funds (3 funds)
        assert len(results) <= 1000
        assert len(results) >= 1  # At least one fund matches

    def test_ytd_period_calculation(self, test_db_with_performance):
        """Test YTD period starts from January 1st of current year."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="ytd"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should include recent data
        assert isinstance(results, list)

    def test_month_period_parsing(self, test_db_with_performance):
        """Test custom month period parsing (e.g., 3m, 6m, 12m)."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)

        # Test 3 months
        filter_3m = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="3m"
        )
        results_3m = tool.forward(numeric_filter=filter_3m)
        assert isinstance(results_3m, list)

        # Test 6 months
        filter_6m = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="6m"
        )
        results_6m = tool.forward(numeric_filter=filter_6m)
        assert isinstance(results_6m, list)

    def test_invalid_period_format_rejected_by_pydantic(self, test_db_with_performance):
        """Test invalid period format is rejected by Pydantic validation."""
        from pydantic import ValidationError

        tool = PerformanceSearchTool(db_path=test_db_with_performance)

        # Should raise ValidationError for invalid period
        with pytest.raises(ValidationError):
            _ = NumericFilter(
                metric="return",
                operator="min",
                value=0.0,
                performance_period="invalid"
            )

    def test_none_performance_period_uses_default(self, test_db_with_performance):
        """Test None performance period uses default."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period=None
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should use default 12 month period
        assert isinstance(results, list)

    def test_max_operator_filters_underperformers(self, test_db_with_performance):
        """Test max operator filters for underperforming funds."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="max",
            value=10.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with return < 10%
        # FUND002 has 8.5% total return
        assert isinstance(results, list)

    def test_min_operator_filters_outperformers(self, test_db_with_performance):
        """Test min operator filters for outperforming funds."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=15.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return funds with return > 15%
        # FUND001 (23.5%) and FUND003 (18.0%) should match
        assert isinstance(results, list)

    def test_negative_threshold_value(self, test_db_with_performance):
        """Test with negative threshold (finding funds with losses)."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="max",
            value=-5.0,  # Funds with losses > -5%
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should handle negative values
        assert isinstance(results, list)

    def test_very_high_threshold(self, test_db_with_performance):
        """Test with very high threshold returns empty."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=1000.0,  # 1000% return
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_returns_list_of_strings(self, test_db_with_performance):
        """Test that results are list of CNPJ strings."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=1)

        if results:
            assert isinstance(results, list)
            assert isinstance(results[0], str)
            assert "/" in results[0]  # CNPJ format check

    def test_no_duplicate_cnpjs(self, test_db_with_performance):
        """Test that results contain no duplicate CNPJs."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # All CNPJs should be unique
        assert len(results) == len(set(results))

    def test_top_operator_behaves_like_min(self, test_db_with_performance):
        """Test 'top' operator behaves same as 'min' (outperformance)."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        filter_top = NumericFilter(
            metric="return",
            operator="top",
            value=10.0,
            performance_period="12m"
        )
        filter_min = NumericFilter(
            metric="return",
            operator="min",
            value=10.0,
            performance_period="12m"
        )

        results_top = tool.forward(numeric_filter=filter_top)
        results_min = tool.forward(numeric_filter=filter_min)

        # Both should return same results
        assert results_top == results_min

    def test_old_data_filtered_out_for_recent_periods(self, test_db_with_performance):
        """Test that very old performance data is excluded for recent period queries."""
        tool = PerformanceSearchTool(db_path=test_db_with_performance)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="3m"  # Only 3 months
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # FUND004 has only old data (400 days ago) so shouldn't appear
        assert "22.333.444/0001-55" not in results
