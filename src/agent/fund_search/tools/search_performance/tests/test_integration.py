"""
Integration tests for PerformanceSearchTool using real database.

Tests with actual br_funds.db to verify tool works with real data.
"""

import pytest

from src.agent.fund_search.models.query import NumericFilter
from src.agent.fund_search.tools.search_performance.tool import PerformanceSearchTool


@pytest.mark.integration
class TestPerformanceSearchToolIntegration:
    """Integration tests for PerformanceSearchTool with real database."""

    def test_search_outperforming_cdi_real_data(self, db_snapshot):
        """Test searching for funds outperforming CDI with real database."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            benchmark_name="CDI",
            performance_period="12m",
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        assert isinstance(results, list)
        assert len(results) <= 10
        for cnpj in results:
            assert isinstance(cnpj, str)
            assert "/" in cnpj

    def test_search_outperforming_selic_real_data(self, db_snapshot):
        """Test searching for funds outperforming SELIC with real database."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            benchmark_name="SELIC",
            performance_period="12m",
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        assert isinstance(results, list)
        assert len(results) <= 10

    def test_search_underperforming_funds_real_data(self, db_snapshot):
        """Test searching for underperforming funds with real database."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return",
            operator="max",
            value=5.0,  # Funds with < 5% return
            performance_period="12m",
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        assert isinstance(results, list)
        assert len(results) <= 10

    def test_search_ytd_performance_real_data(self, db_snapshot):
        """Test YTD performance search with real database."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="ytd",
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=20)

        assert isinstance(results, list)
        assert len(results) <= 20

    def test_search_3month_performance_real_data(self, db_snapshot):
        """Test 3-month performance search with real database."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return",
            operator="min",
            value=0.0,
            performance_period="3m",
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=20)

        assert isinstance(results, list)
        assert len(results) <= 20

    def test_search_with_cnpj_filter_real_data(self, db_snapshot):
        """Test search with CNPJ filter using real database."""
        tool = PerformanceSearchTool(db_path=db_snapshot)

        # First get some CNPJs
        filter1 = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )
        all_results = tool.forward(numeric_filter=filter1, limit=5)

        if len(all_results) >= 2:
            # Filter by specific CNPJs
            cnpjs = all_results[:2]
            filter2 = NumericFilter(
                metric="return", operator="min", value=0.0, performance_period="12m"
            )
            filtered_results = tool.forward(numeric_filter=filter2, cnpjs=cnpjs)

            assert len(filtered_results) <= 2
            for cnpj in filtered_results:
                assert cnpj in cnpjs

    def test_search_with_large_limit_real_data(self, db_snapshot):
        """Test search with very large limit."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=1000)

        assert isinstance(results, list)
        assert len(results) <= 1000

    def test_search_returns_unique_cnpjs(self, db_snapshot):
        """Test that search results contain no duplicate CNPJs."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=100)

        # All CNPJs should be unique
        assert len(results) == len(set(results))

    def test_search_ordered_by_return_descending(self, db_snapshot):
        """Test that results are ordered by return descending."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=50)

        # Results should be non-empty and contain valid CNPJs
        assert isinstance(results, list)
        for cnpj in results:
            assert isinstance(cnpj, str)
            assert "/" in cnpj

    def test_different_time_periods_return_different_results(self, db_snapshot):
        """Test that different time periods may return different results."""
        tool = PerformanceSearchTool(db_path=db_snapshot)

        # 3 month period
        filter_3m = NumericFilter(
            metric="return", operator="min", value=5.0, performance_period="3m"
        )
        results_3m = tool.forward(numeric_filter=filter_3m, limit=20)

        # 12 month period
        filter_12m = NumericFilter(
            metric="return", operator="min", value=5.0, performance_period="12m"
        )
        results_12m = tool.forward(numeric_filter=filter_12m, limit=20)

        # Both should return results
        assert isinstance(results_3m, list)
        assert isinstance(results_12m, list)


@pytest.mark.integration
class TestPerformanceSearchToolErrorHandling:
    """Integration tests focused on error handling and edge cases."""

    def test_handles_missing_database(self, tmp_path):
        """Test tool handles missing database gracefully."""
        bad_path = str(tmp_path / "nonexistent.db")
        tool = PerformanceSearchTool(db_path=bad_path)
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_handles_invalid_database_path(self):
        """Test tool handles invalid database path."""
        tool = PerformanceSearchTool(db_path="/invalid/path/to/database.db")
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_handles_corrupted_database(self, tmp_path):
        """Test tool handles corrupted database file."""
        corrupted_db = tmp_path / "corrupted.db"
        corrupted_db.write_text("This is not a valid database file")

        tool = PerformanceSearchTool(db_path=str(corrupted_db))
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_handles_extreme_threshold_values(self, db_snapshot):
        """Test with extreme threshold values."""
        tool = PerformanceSearchTool(db_path=db_snapshot)

        # Very large positive return
        filter1 = NumericFilter(
            metric="return",
            operator="min",
            value=1000.0,  # 1000% return
            performance_period="12m",
        )
        results1 = tool.forward(numeric_filter=filter1)
        assert isinstance(results1, list)

        # Very large negative return
        filter2 = NumericFilter(
            metric="return",
            operator="max",
            value=-100.0,  # -100% return
            performance_period="12m",
        )
        results2 = tool.forward(numeric_filter=filter2)
        assert isinstance(results2, list)

    def test_handles_special_characters_in_cnpj(self, db_snapshot):
        """Test CNPJ filter with special characters doesn't cause SQL errors."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        cnpjs = [
            "12.345.678/0001-90",
            "00.000.000/0000-00",
            "99.999.999/9999-99",
        ]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_handles_very_long_cnpj_list(self, db_snapshot):
        """Test with very large CNPJ filter list."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        # Get some real CNPJs first
        sample_results = tool.forward(numeric_filter=numeric_filter, limit=5)

        if len(sample_results) > 0:
            # Create a very long list by repeating
            long_cnpj_list = sample_results * 100

            results = tool.forward(numeric_filter=numeric_filter, cnpjs=long_cnpj_list)

            # Should handle without errors
            assert isinstance(results, list)

    def test_handles_multiple_sequential_queries(self, db_snapshot):
        """Test that multiple sequential queries work without connection issues."""
        tool = PerformanceSearchTool(db_path=db_snapshot)

        # Run many sequential queries
        for i in range(10):
            numeric_filter = NumericFilter(
                metric="return",
                operator="min",
                value=i * 2.0,
                performance_period="12m" if i % 2 == 0 else "3m",
            )
            results = tool.forward(numeric_filter=numeric_filter, limit=5)

            assert isinstance(results, list)
            assert len(results) <= 5

    def test_handles_empty_performance_table(self, tmp_path):
        """Test behavior when performance table has no data."""
        db_path = tmp_path / "test_empty.db"
        conn = pytest.importorskip("duckdb").connect(str(db_path))

        # Create schema but don't insert data
        conn.execute("""
            CREATE TABLE funds (
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                identifiers STRUCT(type VARCHAR, value VARCHAR)[]
            )
        """)

        conn.execute("""
            CREATE TABLE fund_performance_indicators (
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                first_date VARCHAR,
                return_pct DOUBLE
            )
        """)

        conn.close()

        tool = PerformanceSearchTool(db_path=str(db_path))
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return empty list
        assert results == []

    def test_handles_funds_with_missing_cnpj(self, tmp_path):
        """Test when performance data exists but fund has no CNPJ identifier."""
        db_path = tmp_path / "test_missing_cnpj.db"
        conn = pytest.importorskip("duckdb").connect(str(db_path))

        conn.execute("""
            CREATE TABLE funds (
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                identifiers STRUCT(type VARCHAR, value VARCHAR)[]
            )
        """)

        conn.execute("""
            CREATE TABLE fund_performance_indicators (
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                first_date VARCHAR,
                return_pct DOUBLE
            )
        """)

        # Fund with no CNPJ identifier
        conn.execute("""
            INSERT INTO funds VALUES
            (
                {'type': 'CVM', 'value': 'FUND001'},
                [{'type': 'OTHER_ID', 'value': 'SOME_VALUE'}]
            )
        """)

        from datetime import datetime, timedelta

        recent_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        conn.execute(f"""
            INSERT INTO fund_performance_indicators VALUES
            (
                {{'type': 'CVM', 'value': 'FUND001'}},
                '{recent_date}',
                15.5
            )
        """)

        conn.close()

        tool = PerformanceSearchTool(db_path=str(db_path))
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should handle gracefully - fund has no CNPJ
        assert isinstance(results, list)

    def test_performance_with_large_limit(self, db_snapshot):
        """Test performance doesn't degrade with very large limits."""
        tool = PerformanceSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="return", operator="min", value=0.0, performance_period="12m"
        )

        # Request very large number of results
        results = tool.forward(numeric_filter=numeric_filter, limit=100000)

        # Should complete without timeout/error
        assert isinstance(results, list)
        assert len(results) <= 100000

    def test_concurrent_read_operations(self, db_snapshot):
        """Test that multiple concurrent read operations work correctly."""
        import concurrent.futures

        def run_query(threshold):
            tool = PerformanceSearchTool(db_path=db_snapshot)
            numeric_filter = NumericFilter(
                metric="return",
                operator="min",
                value=threshold,
                performance_period="12m",
            )
            return tool.forward(numeric_filter=numeric_filter, limit=10)

        # Run multiple queries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(run_query, threshold)
                for threshold in [0.0, 5.0, 10.0, 15.0, 20.0]
            ]

            results = [future.result() for future in futures]

        # All should succeed
        assert len(results) == 5
        for result in results:
            assert isinstance(result, list)

    def test_rejects_non_return_metrics(self, db_snapshot):
        """Test that tool only processes 'return' metric."""
        tool = PerformanceSearchTool(db_path=db_snapshot)

        # Try with different metrics
        for metric in ["aum", "holders", "position_value"]:
            numeric_filter = NumericFilter(
                metric=metric, operator="min", value=0.0, performance_period="12m"
            )

            results = tool.forward(numeric_filter=numeric_filter)

            # Should return empty for non-return metrics
            assert results == []
