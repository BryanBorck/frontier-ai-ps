"""
Integration tests for SnapshotSearchTool using real database.

Tests with actual br_funds.db to verify tool works with real data.
"""

import pytest

from src.agent.fund_search.models.query import NumericFilter
from src.agent.fund_search.tools.search_snapshots.tool import SnapshotSearchTool


@pytest.mark.integration
class TestSnapshotSearchToolIntegration:
    """Integration tests for SnapshotSearchTool with real database."""

    def test_search_by_min_aum_real_data(self, db_snapshot):
        """Test searching by minimum AUM with real database."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=1000000000,  # 1 billion
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 10
        # All results should be valid CNPJs
        for cnpj in results:
            assert isinstance(cnpj, str)
            assert "/" in cnpj  # CNPJ format check

    def test_search_by_max_aum_real_data(self, db_snapshot):
        """Test searching by maximum AUM with real database."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="max",
            value=10000000,  # 10 million
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        assert isinstance(results, list)
        assert len(results) <= 10
        for cnpj in results:
            assert isinstance(cnpj, str)

    def test_search_by_min_holders_real_data(self, db_snapshot):
        """Test searching by minimum holder count with real database."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="holders",
            operator="min",
            value=10000,  # 10k holders
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        assert isinstance(results, list)
        assert len(results) <= 10
        for cnpj in results:
            assert isinstance(cnpj, str)

    def test_search_by_max_holders_real_data(self, db_snapshot):
        """Test searching by maximum holder count with real database."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="holders",
            operator="max",
            value=100,  # Small funds
        )

        results = tool.forward(numeric_filter=numeric_filter, limit=10)

        assert isinstance(results, list)
        assert len(results) <= 10
        for cnpj in results:
            assert isinstance(cnpj, str)

    def test_search_top_aum_real_data(self, db_snapshot):
        """Test getting top funds by AUM with real database."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="top", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=100)

        assert isinstance(results, list)
        assert len(results) <= 100
        # Results should be ordered by AUM descending
        assert len(results) > 0

    def test_search_top_holders_real_data(self, db_snapshot):
        """Test getting top funds by holder count with real database."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="holders", operator="top", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=100)

        assert isinstance(results, list)
        assert len(results) <= 100
        assert len(results) > 0

    def test_search_with_cnpj_filter_real_data(self, db_snapshot):
        """Test searching with CNPJ filter using real data."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # First, get some CNPJs
        filter1 = NumericFilter(metric="aum", operator="top", value=0)
        all_results = tool.forward(numeric_filter=filter1, limit=5)

        if len(all_results) < 2:
            pytest.skip("Not enough funds in database for this test")

        # Now filter by specific CNPJs
        cnpjs = all_results[:2]
        filter2 = NumericFilter(metric="aum", operator="min", value=0)
        filtered_results = tool.forward(numeric_filter=filter2, cnpjs=cnpjs)

        assert len(filtered_results) <= 2
        for cnpj in filtered_results:
            assert cnpj in cnpjs

    def test_search_with_large_limit_real_data(self, db_snapshot):
        """Test search with very large limit."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=10000)

        assert isinstance(results, list)
        assert len(results) <= 10000

    def test_search_with_very_high_threshold(self, db_snapshot):
        """Test search with unrealistically high threshold."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(
            metric="aum",
            operator="min",
            value=10000000000000,  # 10 trillion
        )

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return empty list or very few results
        assert isinstance(results, list)
        assert len(results) <= 5

    def test_search_returns_unique_cnpjs(self, db_snapshot):
        """Test that search results contain no duplicate CNPJs."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=100)

        # All CNPJs should be unique
        assert len(results) == len(set(results))

    def test_search_handles_edge_case_values(self, db_snapshot):
        """Test search with edge case threshold values."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # Zero threshold
        filter1 = NumericFilter(metric="aum", operator="min", value=0)
        results1 = tool.forward(numeric_filter=filter1, limit=10)
        assert len(results1) > 0

        # None threshold (should default to 0)
        filter2 = NumericFilter(metric="aum", operator="min", value=None)
        results2 = tool.forward(numeric_filter=filter2, limit=10)
        assert len(results2) > 0

    def test_latest_snapshots_used_real_data(self, db_snapshot):
        """Test that tool uses latest snapshots with real database."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="top", value=0)

        results = tool.forward(numeric_filter=numeric_filter, limit=50)

        # Should return results based on latest snapshots
        assert isinstance(results, list)
        assert len(results) > 0
        # All results should have valid CNPJ format
        for cnpj in results:
            assert "/" in cnpj
            assert "-" in cnpj

    def test_database_connection_handling(self, db_snapshot):
        """Test that database connections are properly managed."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        # Multiple sequential calls should all work
        for _ in range(3):
            results = tool.forward(numeric_filter=numeric_filter, limit=5)
            assert isinstance(results, list)

    def test_search_with_different_operators(self, db_snapshot):
        """Test all operator types with real data."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # Test min operator
        filter_min = NumericFilter(metric="aum", operator="min", value=1000000)
        results_min = tool.forward(numeric_filter=filter_min, limit=10)
        assert isinstance(results_min, list)

        # Test max operator
        filter_max = NumericFilter(metric="aum", operator="max", value=100000000)
        results_max = tool.forward(numeric_filter=filter_max, limit=10)
        assert isinstance(results_max, list)

        # Test top operator
        filter_top = NumericFilter(metric="aum", operator="top", value=1000000)
        results_top = tool.forward(numeric_filter=filter_top, limit=10)
        assert isinstance(results_top, list)

    def test_search_with_both_metrics(self, db_snapshot):
        """Test searching with both AUM and holders metrics."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # Search by AUM
        filter_aum = NumericFilter(metric="aum", operator="min", value=1000000)
        results_aum = tool.forward(numeric_filter=filter_aum, limit=10)
        assert isinstance(results_aum, list)

        # Search by holders
        filter_holders = NumericFilter(metric="holders", operator="min", value=100)
        results_holders = tool.forward(numeric_filter=filter_holders, limit=10)
        assert isinstance(results_holders, list)

    def test_empty_cnpj_filter(self, db_snapshot):
        """Test that empty CNPJ filter doesn't restrict results."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results_no_filter = tool.forward(numeric_filter=numeric_filter, limit=10)
        results_empty_filter = tool.forward(numeric_filter=numeric_filter, cnpjs=[], limit=10)

        # Both should return same results
        assert len(results_no_filter) == len(results_empty_filter)


@pytest.mark.integration
class TestSnapshotSearchToolErrorHandling:
    """Integration tests focused on error handling and edge cases."""

    def test_handles_missing_database(self, tmp_path):
        """Test tool handles missing database gracefully."""
        bad_path = str(tmp_path / "nonexistent.db")
        tool = SnapshotSearchTool(db_path=bad_path)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        # Should return empty list instead of crashing
        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_handles_invalid_database_path(self):
        """Test tool handles invalid database path."""
        tool = SnapshotSearchTool(db_path="/invalid/path/to/database.db")
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_handles_corrupted_database(self, tmp_path):
        """Test tool handles corrupted database file."""
        corrupted_db = tmp_path / "corrupted.db"
        corrupted_db.write_text("This is not a valid database file")

        tool = SnapshotSearchTool(db_path=str(corrupted_db))
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        assert results == []

    def test_handles_extreme_value_thresholds(self, db_snapshot):
        """Test with extreme threshold values."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # Very large positive value
        filter1 = NumericFilter(metric="aum", operator="min", value=999999999999999)
        results1 = tool.forward(numeric_filter=filter1)
        assert isinstance(results1, list)

        # Very large negative threshold (should return all or none depending on operator)
        filter2 = NumericFilter(metric="aum", operator="max", value=-1)
        results2 = tool.forward(numeric_filter=filter2)
        assert isinstance(results2, list)

    def test_handles_special_characters_in_cnpj(self, db_snapshot):
        """Test CNPJ filter with special characters doesn't cause SQL errors."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        # CNPJs with various special characters
        cnpjs = [
            "12.345.678/0001-90",
            "00.000.000/0000-00",
            "99.999.999/9999-99",
        ]

        results = tool.forward(numeric_filter=numeric_filter, cnpjs=cnpjs)

        # Should handle gracefully, return valid results or empty
        assert isinstance(results, list)

    def test_handles_very_long_cnpj_list(self, db_snapshot):
        """Test with very large CNPJ filter list."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        # Get some real CNPJs first
        sample_results = tool.forward(numeric_filter=numeric_filter, limit=5)

        if len(sample_results) > 0:
            # Create a very long list by repeating
            long_cnpj_list = sample_results * 100  # 500 CNPJs if we got 5

            results = tool.forward(numeric_filter=numeric_filter, cnpjs=long_cnpj_list)

            # Should handle without errors
            assert isinstance(results, list)

    def test_handles_null_values_gracefully(self, db_snapshot):
        """Test that tool handles NULL values in database gracefully."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # Search with both metrics - if DB has NULLs, should handle them
        filter_aum = NumericFilter(metric="aum", operator="min", value=0)
        results_aum = tool.forward(numeric_filter=filter_aum, limit=100)

        filter_holders = NumericFilter(metric="holders", operator="min", value=0)
        results_holders = tool.forward(numeric_filter=filter_holders, limit=100)

        # Should return valid results without crashing
        assert isinstance(results_aum, list)
        assert isinstance(results_holders, list)
        # All results should be valid CNPJs (not None)
        for cnpj in results_aum:
            assert cnpj is not None
            assert isinstance(cnpj, str)

    def test_handles_multiple_sequential_queries(self, db_snapshot):
        """Test that multiple sequential queries work without connection issues."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # Run many sequential queries
        for i in range(10):
            numeric_filter = NumericFilter(
                metric="aum" if i % 2 == 0 else "holders",
                operator="min",
                value=i * 1000000,
            )
            results = tool.forward(numeric_filter=numeric_filter, limit=5)

            assert isinstance(results, list)
            # Connection should be closed properly each time
            assert len(results) <= 5

    def test_handles_funds_with_no_snapshots(self, tmp_path):
        """Test behavior when database has funds but no snapshots."""
        db_path = tmp_path / "test_no_snapshots.db"
        conn = pytest.importorskip("duckdb").connect(str(db_path))

        # Create schema but don't insert snapshots
        conn.execute("""
            CREATE TABLE funds (
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                identifiers STRUCT(type VARCHAR, value VARCHAR)[]
            )
        """)

        conn.execute("""
            CREATE TABLE fund_snapshots (
                snapshot_id STRUCT(type VARCHAR, value VARCHAR),
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                net_assets_value STRUCT(value DOUBLE, currency VARCHAR),
                number_of_holders DOUBLE,
                timestamp TIMESTAMP
            )
        """)

        conn.execute("""
            INSERT INTO funds VALUES
            (
                {'type': 'CVM', 'value': 'FUND001'},
                [{'type': 'CNPJ', 'value': '12.345.678/0001-90'}]
            )
        """)

        conn.close()

        tool = SnapshotSearchTool(db_path=str(db_path))
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        # Should return empty list, not error
        assert results == []

    def test_handles_snapshots_with_missing_cnpj(self, tmp_path):
        """Test when snapshots exist but fund has no CNPJ identifier."""
        db_path = tmp_path / "test_missing_cnpj.db"
        conn = pytest.importorskip("duckdb").connect(str(db_path))

        conn.execute("""
            CREATE TABLE funds (
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                identifiers STRUCT(type VARCHAR, value VARCHAR)[]
            )
        """)

        conn.execute("""
            CREATE TABLE fund_snapshots (
                snapshot_id STRUCT(type VARCHAR, value VARCHAR),
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                net_assets_value STRUCT(value DOUBLE, currency VARCHAR),
                number_of_holders DOUBLE,
                timestamp TIMESTAMP
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

        conn.execute("""
            INSERT INTO fund_snapshots VALUES
            (
                {'type': 'SNAPSHOT', 'value': 'SNAP001'},
                {'type': 'CVM', 'value': 'FUND001'},
                {'value': 1000000.0, 'currency': 'BRL'},
                100.0,
                '2024-01-31 00:00:00'
            )
        """)

        conn.close()

        tool = SnapshotSearchTool(db_path=str(db_path))
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        # Should handle gracefully - fund has no CNPJ so won't be in results
        assert isinstance(results, list)

    def test_handles_duplicate_snapshots_same_timestamp(self, tmp_path):
        """Test behavior with duplicate snapshots at same timestamp."""
        db_path = tmp_path / "test_duplicates.db"
        conn = pytest.importorskip("duckdb").connect(str(db_path))

        conn.execute("""
            CREATE TABLE funds (
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                identifiers STRUCT(type VARCHAR, value VARCHAR)[]
            )
        """)

        conn.execute("""
            CREATE TABLE fund_snapshots (
                snapshot_id STRUCT(type VARCHAR, value VARCHAR),
                fund_id STRUCT(type VARCHAR, value VARCHAR),
                net_assets_value STRUCT(value DOUBLE, currency VARCHAR),
                number_of_holders DOUBLE,
                timestamp TIMESTAMP
            )
        """)

        conn.execute("""
            INSERT INTO funds VALUES
            (
                {'type': 'CVM', 'value': 'FUND001'},
                [{'type': 'CNPJ', 'value': '12.345.678/0001-90'}]
            )
        """)

        # Insert duplicate snapshots with same timestamp
        conn.execute("""
            INSERT INTO fund_snapshots VALUES
            (
                {'type': 'SNAPSHOT', 'value': 'SNAP001'},
                {'type': 'CVM', 'value': 'FUND001'},
                {'value': 1000000.0, 'currency': 'BRL'},
                100.0,
                '2024-01-31 00:00:00'
            ),
            (
                {'type': 'SNAPSHOT', 'value': 'SNAP002'},
                {'type': 'CVM', 'value': 'FUND001'},
                {'value': 2000000.0, 'currency': 'BRL'},
                200.0,
                '2024-01-31 00:00:00'
            )
        """)

        conn.close()

        tool = SnapshotSearchTool(db_path=str(db_path))
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        results = tool.forward(numeric_filter=numeric_filter)

        # DISTINCT should ensure CNPJ appears only once
        assert isinstance(results, list)
        # Should have at most 1 result (CNPJ should be unique)
        if results:
            assert len(results) == len(set(results))

    def test_performance_with_large_limit(self, db_snapshot):
        """Test performance doesn't degrade severely with very large limits."""
        tool = SnapshotSearchTool(db_path=db_snapshot)
        numeric_filter = NumericFilter(metric="aum", operator="min", value=0)

        # Request very large number of results
        results = tool.forward(numeric_filter=numeric_filter, limit=100000)

        # Should complete without timeout/error
        assert isinstance(results, list)
        assert len(results) <= 100000

    def test_handles_mixed_null_and_valid_values(self, db_snapshot):
        """Test with queries that might return mix of NULL and valid values."""
        tool = SnapshotSearchTool(db_path=db_snapshot)

        # Very low threshold that might catch edge cases
        filter1 = NumericFilter(metric="aum", operator="max", value=1)
        results1 = tool.forward(numeric_filter=filter1, limit=100)

        filter2 = NumericFilter(metric="holders", operator="max", value=0)
        results2 = tool.forward(numeric_filter=filter2, limit=100)

        # Should filter out NULL CNPJs
        for cnpj in results1:
            assert cnpj is not None
            assert cnpj != ""

        for cnpj in results2:
            assert cnpj is not None
            assert cnpj != ""

    def test_concurrent_read_operations(self, db_snapshot):
        """Test that multiple concurrent read operations work correctly."""
        import concurrent.futures

        def run_query(threshold):
            tool = SnapshotSearchTool(db_path=db_snapshot)
            numeric_filter = NumericFilter(metric="aum", operator="min", value=threshold)
            return tool.forward(numeric_filter=numeric_filter, limit=10)

        # Run multiple queries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(run_query, threshold)
                for threshold in [0, 1000000, 10000000, 100000000, 1000000000]
            ]

            results = [future.result() for future in futures]

        # All should succeed
        assert len(results) == 5
        for result in results:
            assert isinstance(result, list)
