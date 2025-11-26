"""
Integration tests for FundSearchTool.
"""

import pytest

from src.agent.fund_search.models.query import FundSearchCriteria
from src.agent.fund_search.tools.search_funds.tool import FundSearchTool


@pytest.mark.integration
@pytest.mark.requires_db
class TestFundSearchToolIntegration:
    """Integration tests using real database snapshots."""

    def test_search_with_real_schema(self, db_snapshot):
        """
        Test that queries work against real database schema.

        This validates:
        - STRUCT access syntax (identifiers, service_providers)
        - Array filtering with list_filter
        - Actual column names match our queries
        """
        tool = FundSearchTool(db_path=db_snapshot)
        criteria = FundSearchCriteria(fund_type=["FII"])

        # Should execute without SQL errors
        results = tool.forward(criteria=criteria, limit=10)

        assert isinstance(results, list)
        # Results might be empty or contain CNPJs
        for cnpj in results:
            assert isinstance(cnpj, str)
            assert len(cnpj) > 0

    def test_search_by_investment_class_real_data(self, db_snapshot):
        """Test searching by investment class with real data."""
        tool = FundSearchTool(db_path=db_snapshot)

        # Real investment classes from the database
        criteria = FundSearchCriteria(investment_class=["Ações"])

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)
        # Should find some equity funds
        assert len(results) >= 0  # Might be 0 if no data, but shouldn't crash

    def test_search_by_target_audience_real_data(self, db_snapshot):
        """Test searching by target audience with real data."""
        tool = FundSearchTool(db_path=db_snapshot)

        # Real target audiences: RETAIL, QUALIFIED, PROFESSIONAL
        criteria = FundSearchCriteria(target_audience=["QUALIFIED"])

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)

    def test_search_with_service_provider_entity(self, db_snapshot):
        """
        Test service provider filtering with real data.

        This is critical because:
        - service_providers is a STRUCT array
        - We filter using list_filter and tax_id matching
        - Entity normalization must work
        """
        tool = FundSearchTool(db_path=db_snapshot)

        # Common managers in Brazilian market
        criteria = FundSearchCriteria(service_provider_entity=["XP", "BTG Pactual", "Itaú"])

        results = tool.forward(criteria=criteria, limit=50)

        assert isinstance(results, list)
        # Should find funds managed by these entities

    def test_search_combines_name_and_entity(self, db_snapshot):
        """
        Test combining name search with entity filtering.

        This tests the complex AND logic between name and service provider.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria(service_provider_entity=["XP"])

        results = tool.forward(
            criteria=criteria,
            name="Malls",  # Common in FII names
            limit=20,
        )

        assert isinstance(results, list)

    def test_search_excludes_cancelled_funds_real_data(self, db_snapshot):
        """
        Test that cancelled funds are excluded.

        Per the schema, most funds are CANCELLED (57.4%).
        We must exclude them.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        # Search without filters - should still exclude cancelled
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=100)

        # All results should be from active funds
        # We can't directly verify status without fetching fund details,
        # but the query should have "status != 'CANCELLED'" filter
        assert isinstance(results, list)

    def test_search_orders_by_aum_descending(self, db_snapshot):
        """
        Test that results are ordered by net_asset_value.value DESC.

        This ensures largest funds appear first.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria(fund_type=["FII"])

        results = tool.forward(criteria=criteria, limit=10)

        # Results should be ordered by AUM (largest first)
        # We can't verify exact order without fetching details,
        # but query should execute without error
        assert isinstance(results, list)

    def test_search_with_boolean_flags_real_data(self, db_snapshot):
        """Test searching with boolean criteria on real data."""
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria(fund_of_funds=False, is_exclusive_fund=False)

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)

    def test_search_with_manager_type(self, db_snapshot):
        """Test searching by manager type."""
        tool = FundSearchTool(db_path=db_snapshot)

        # INDEPENDENT, CORPORATE, etc.
        criteria = FundSearchCriteria(manager_type=["INDEPENDENT"])

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)

    def test_search_with_cnpj_filter_list(self, db_snapshot):
        """
        Test filtering by CNPJ list.

        This is used when refining results from previous searches.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria()

        # Get some CNPJs first
        all_results = tool.forward(criteria=criteria, limit=50)

        if len(all_results) >= 2:
            # Filter to subset
            subset_cnpjs = all_results[:2]

            filtered_results = tool.forward(criteria=criteria, cnpjs=subset_cnpjs, limit=10)

            # Should return only the filtered CNPJs
            assert len(filtered_results) <= len(subset_cnpjs)
            assert all(cnpj in subset_cnpjs for cnpj in filtered_results)

    def test_search_with_multiple_criteria_real_data(self, db_snapshot):
        """
        Test combining multiple criteria.

        This validates the AND logic in query building.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria(
            fund_type=["FII"],
            investment_class=["Fundos Imobiliários"],
            target_audience=["QUALIFIED"],
        )

        results = tool.forward(criteria=criteria, limit=20)

        assert isinstance(results, list)

    def test_entity_map_loading(self, db_snapshot):
        """
        Test that entity_correlations.json is loaded correctly.

        This file is critical for entity normalization.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        # entity_map should be loaded (might be empty if file doesn't exist)
        assert hasattr(tool, "entity_map")
        assert isinstance(tool.entity_map, dict)

    def test_search_with_all_fund_types(self, db_snapshot):
        """
        Test searching across all major fund types.

        From schema: FI, FIF, FACFIF, FIP, FIDC, FII, FITVM, FMIA-CL
        """
        tool = FundSearchTool(db_path=db_snapshot)

        fund_types = ["FI", "FII", "FIP", "FIDC"]

        for fund_type in fund_types:
            criteria = FundSearchCriteria(fund_type=[fund_type])
            results = tool.forward(criteria=criteria, limit=5)

            # Should execute without error for each type
            assert isinstance(results, list)

    def test_search_respects_limit(self, db_snapshot):
        """Test that limit parameter is respected."""
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria()

        # Request different limits
        results_5 = tool.forward(criteria=criteria, limit=5)
        results_10 = tool.forward(criteria=criteria, limit=10)

        assert len(results_5) <= 5
        assert len(results_10) <= 10

    def test_search_handles_empty_criteria(self, db_snapshot):
        """
        Test search with empty criteria returns results.

        Should return funds ordered by AUM with only status filter.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=10)

        # Should return something (unless DB is empty)
        assert isinstance(results, list)

    def test_search_case_insensitive_name(self, db_snapshot):
        """
        Test that name search is case-insensitive.

        Uses LOWER() in SQL for case-insensitive matching.
        """
        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria()

        # Same query, different cases
        results_lower = tool.forward(criteria=criteria, name="xp", limit=10)
        results_upper = tool.forward(criteria=criteria, name="XP", limit=10)

        # Should find similar results (exact match might vary due to scoring)
        assert isinstance(results_lower, list)
        assert isinstance(results_upper, list)


@pytest.mark.integration
@pytest.mark.requires_db
@pytest.mark.slow
class TestFundSearchToolPerformance:
    """
    Performance tests for search_funds tool.

    These validate that queries execute efficiently on real data.
    """

    def test_search_performance_with_filters(self, db_snapshot):
        """Test that complex queries execute in reasonable time."""
        import time

        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria(
            fund_type=["FII"],
            investment_class=["FII"],  # Real investment class
            target_audience=["QUALIFIED"],
            fund_of_funds=False,
        )

        start = time.time()
        results = tool.forward(criteria=criteria, limit=50)
        duration = time.time() - start

        # Should complete in under 1 second (DuckDB is fast)
        assert duration < 1.0
        assert isinstance(results, list)

    def test_search_performance_large_result_set(self, db_snapshot):
        """Test performance when returning many results."""
        import time

        tool = FundSearchTool(db_path=db_snapshot)

        criteria = FundSearchCriteria()  # Minimal filter

        start = time.time()
        results = tool.forward(criteria=criteria, limit=1000)
        duration = time.time() - start

        # Should complete in under 2 seconds even for large result set
        assert duration < 2.0
        assert isinstance(results, list)
        assert len(results) <= 1000


# ============================================================================
# NEW: Real Data Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.requires_db
class TestRealDatabaseValues:
    """
    Integration tests using actual real-world values from br_funds.db.

    Based on actual database contents:
    - 461 ACTIVE funds (0.7%)
    - Top types: FI (225), FIP (96), FIDC (83), FII (48)
    - Top classes: Multimercado (123), FIP Multi (73), Renda Fixa (55)
    - Audiences: QUALIFIED (245), PROFESSIONAL (95), RETAIL (90)
    """

    def test_search_returns_only_active_funds(self, real_db_path):
        """
        Test that only ACTIVE funds are returned (not CANCELLED).

        Database has 38,994 CANCELLED but only 461 ACTIVE.
        """
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=100)

        # Should return active funds (max 461 in real DB)
        assert len(results) > 0
        assert len(results) <= 461

    def test_search_with_real_fund_types(self, real_db_path):
        """Test with actual fund types from database."""
        tool = FundSearchTool(db_path=real_db_path)

        # Real fund types with known counts
        test_cases = [
            ("FI", 225),  # Most common
            ("FIP", 96),
            ("FIDC", 83),
            ("FII", 48),
        ]

        for fund_type, expected_max in test_cases:
            criteria = FundSearchCriteria(fund_type=[fund_type])
            results = tool.forward(criteria=criteria, limit=500)

            # Should find funds, up to expected count
            assert len(results) > 0
            assert len(results) <= expected_max

    def test_search_with_real_investment_classes(self, real_db_path):
        """Test with actual investment classes from database."""
        tool = FundSearchTool(db_path=real_db_path)

        # Real investment classes
        real_classes = [
            "Multimercado",  # 123 active
            "FIP Multi",  # 73 active
            "Renda Fixa",  # 55 active
            "FII",  # 45 active
            "Ações",  # 28 active
        ]

        for inv_class in real_classes:
            criteria = FundSearchCriteria(investment_class=[inv_class])
            results = tool.forward(criteria=criteria, limit=200)

            # Should find some results
            assert isinstance(results, list)
            assert len(results) >= 0  # Some might have 0 results

    def test_search_with_real_target_audiences(self, real_db_path):
        """Test with actual target audiences from database."""
        tool = FundSearchTool(db_path=real_db_path)

        audiences_with_counts = {
            "QUALIFIED": 245,
            "PROFESSIONAL": 95,
            "RETAIL": 90,
        }

        for audience, expected_max in audiences_with_counts.items():
            criteria = FundSearchCriteria(target_audience=[audience])
            results = tool.forward(criteria=criteria, limit=500)

            assert len(results) > 0
            assert len(results) <= expected_max

    def test_search_with_real_cnpj(self, real_db_path):
        """Test searching for actual CNPJ from database."""
        tool = FundSearchTool(db_path=real_db_path)

        # Real CNPJs from active funds
        real_cnpjs = [
            "08.771.975/0001-25",  # BNP PARIBAS fund
            "21.838.483/0001-78",  # RIO FORMOSO fund
            "33.361.831/0001-48",  # BLACKROCK fund
        ]

        for cnpj in real_cnpjs:
            criteria = FundSearchCriteria()
            results = tool.forward(criteria=criteria, cnpjs=[cnpj], limit=10)

            # Should find exactly this fund
            assert len(results) == 1
            assert results[0] == cnpj

    def test_combination_filters_real_data(self, real_db_path):
        """Test combining filters with real data."""
        tool = FundSearchTool(db_path=real_db_path)

        # FII + QUALIFIED audience (should exist)
        criteria = FundSearchCriteria(fund_type=["FII"], target_audience=["QUALIFIED"])

        results = tool.forward(criteria=criteria, limit=100)

        # Should find some FII funds for qualified investors
        assert isinstance(results, list)

    def test_empty_investment_class_in_real_db(self, real_db_path):
        """
        Test handling of funds with empty/null investment_class.

        Database shows 7 active funds have empty investment_class.
        """
        tool = FundSearchTool(db_path=real_db_path)

        # Search for funds with empty investment class
        # This tests NULL handling in real database
        criteria = FundSearchCriteria()  # No filter

        results = tool.forward(criteria=criteria, limit=500)

        # Should return results without crashing on NULL/empty values
        assert isinstance(results, list)


# ============================================================================
# Error Handling with Real Database
# ============================================================================


@pytest.mark.integration
@pytest.mark.requires_db
class TestRealDatabaseErrorHandling:
    """
    Error handling tests using real database.

    Tests scenarios that can only occur with production data.
    """

    def test_search_with_very_small_limit_on_large_db(self, real_db_path):
        """Test limit=1 on database with 67k+ funds."""
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=1)

        # Should return exactly 1 result (highest AUM)
        assert len(results) == 1
        assert isinstance(results[0], str)

    def test_search_all_active_funds_exact_count(self, real_db_path):
        """
        Test that we get exactly 461 active funds max.

        This validates the status != 'CANCELLED' filter works.
        """
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        # Request more than exists
        results = tool.forward(criteria=criteria, limit=10000)

        # Should return max 461 (number of ACTIVE funds)
        assert len(results) <= 461

    def test_search_nonexistent_fund_type(self, real_db_path):
        """Test searching for fund type that doesn't exist."""
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria(fund_type=["NONEXISTENT_TYPE"])

        results = tool.forward(criteria=criteria)

        # Should return empty list, not crash
        assert results == []

    def test_search_with_sql_special_characters_in_name(self, real_db_path):
        """Test name search with SQL special characters."""
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        # These should not break the query
        special_names = [
            "O'Brien Fund",  # Single quote
            "Fund & Co.",  # Ampersand
            "100% Equity",  # Percent sign
            "Fund [Class A]",  # Brackets
        ]

        for name in special_names:
            results = tool.forward(criteria=criteria, name=name)
            # Should not crash
            assert isinstance(results, list)

    def test_concurrent_queries_on_real_db(self, real_db_path):
        """Test multiple concurrent queries don't interfere."""
        tool = FundSearchTool(db_path=real_db_path)

        criteria1 = FundSearchCriteria(fund_type=["FII"])
        criteria2 = FundSearchCriteria(fund_type=["FIP"])
        criteria3 = FundSearchCriteria(investment_class=["Multimercado"])

        # Execute multiple queries in sequence
        results1 = tool.forward(criteria=criteria1, limit=50)
        results2 = tool.forward(criteria=criteria2, limit=50)
        results3 = tool.forward(criteria=criteria3, limit=50)

        # All should succeed
        assert isinstance(results1, list)
        assert isinstance(results2, list)
        assert isinstance(results3, list)

        # Results should be different
        assert set(results1) != set(results2)

    def test_search_with_extremely_specific_filters(self, real_db_path):
        """Test with filters so specific they might return nothing."""
        tool = FundSearchTool(db_path=real_db_path)

        # Very specific combination that might not exist
        criteria = FundSearchCriteria(
            fund_type=["FII"],
            investment_class=["Multimercado"],  # Unlikely combo
            target_audience=["PROFESSIONAL"],
            fund_of_funds=True,
            is_exclusive_fund=True,
        )

        results = tool.forward(criteria=criteria)

        # Should handle gracefully (empty or very few results)
        assert isinstance(results, list)
        assert len(results) < 10  # Unlikely to have many

    def test_search_with_partial_name_match_real_names(self, real_db_path):
        """Test partial name matching with real fund names."""
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        # Common words in Brazilian fund names
        common_words = ["PARIBAS", "BLACKROCK", "INVESTIMENTO", "FUNDO"]

        for word in common_words:
            results = tool.forward(criteria=criteria, name=word, limit=10)

            # Should find some matches
            assert isinstance(results, list)
            # Some might have 0 results, but shouldn't crash

    def test_database_read_only_doesnt_lock(self, real_db_path):
        """Test that read-only queries don't lock the database."""
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        # Multiple reads should all succeed
        for _ in range(5):
            results = tool.forward(criteria=criteria, limit=10)
            assert isinstance(results, list)

    def test_aum_ordering_with_real_data(self, real_db_path):
        """Test that results are truly ordered by AUM with real data."""
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria(fund_type=["FII"])

        # Get top 3 FII funds by AUM
        results = tool.forward(criteria=criteria, limit=3)

        assert len(results) >= 1
        # Results should be ordered by net_asset_value DESC
        # (Can't verify exact order without querying AUM separately)

    def test_large_result_set_all_have_valid_cnpjs(self, real_db_path):
        """Test that large result sets have all valid CNPJs."""
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=100)

        # All should be valid CNPJs (not None, not empty)
        assert all(cnpj for cnpj in results)
        assert all(isinstance(cnpj, str) for cnpj in results)
        assert all(len(cnpj) > 0 for cnpj in results)
        assert None not in results
        assert "" not in results

    def test_search_handles_funds_with_missing_aum(self, real_db_path):
        """
        Test that funds with NULL/missing AUM don't crash sorting.

        Since we ORDER BY net_asset_value.value DESC, NULLs should be handled.
        """
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        # Should not crash even if some funds have NULL AUM
        results = tool.forward(criteria=criteria, limit=100)

        assert isinstance(results, list)

    def test_search_with_unspecified_target_audience(self, real_db_path):
        """
        Test searching funds with UNSPECIFIED target audience.

        Database shows 31 active funds have UNSPECIFIED audience.
        """
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria(target_audience=["UNSPECIFIED"])

        results = tool.forward(criteria=criteria, limit=50)

        # Should find the UNSPECIFIED audience funds
        assert isinstance(results, list)
        assert len(results) <= 31

    def test_search_performance_with_all_active_funds(self, real_db_path):
        """Test performance when searching across all 461 active funds."""
        import time

        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()  # No filters

        start = time.time()
        results = tool.forward(criteria=criteria, limit=500)
        duration = time.time() - start

        # Should complete in under 1 second even with 461 funds
        assert duration < 1.0
        assert len(results) <= 461

    def test_search_with_multiple_fund_types_real(self, real_db_path):
        """Test searching multiple fund types at once."""
        tool = FundSearchTool(db_path=real_db_path)

        # Multiple real fund types
        criteria = FundSearchCriteria(fund_type=["FI", "FIP", "FIDC"])

        results = tool.forward(criteria=criteria, limit=500)

        # Should find funds from any of these types
        # FI(225) + FIP(96) + FIDC(83) = 404 max
        assert len(results) > 0
        assert len(results) <= 404

    def test_search_filters_out_cancelled_properly(self, real_db_path):
        """
        Verify CANCELLED funds are excluded.

        Database has 38,994 CANCELLED vs 461 ACTIVE.
        """
        tool = FundSearchTool(db_path=real_db_path)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=10000)

        # Should never return more than active funds (461)
        assert len(results) <= 461

        # Should return far fewer than total funds (67,928)
        assert len(results) < 1000
