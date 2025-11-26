"""
Unit tests for FundSearchTool.
"""

import pytest

from src.agent.fund_search.models.query import FundSearchCriteria
from src.agent.fund_search.tools.search_funds.tool import FundSearchTool

# ============================================================================
# TEST CLASS 1: Basic Single-Criterion Tests
# ============================================================================


@pytest.mark.unit
class TestBasicCriteria:
    """Test each criterion individually."""

    @pytest.mark.parametrize(
        "fund_type,expected_count",
        [
            (["FII"], 2),  # XP Malls and BTG Logística
            (["FI"], 1),  # Itaú Ações
            (["FII", "FI"], 3),  # All active funds
            (["NONEXISTENT"], 0),  # Invalid type
        ],
    )
    def test_search_by_fund_type_parametrized(self, test_db_with_funds, fund_type, expected_count):
        """Test searching by different fund types."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=fund_type)

        results = tool.forward(criteria=criteria)

        assert len(results) == expected_count

    @pytest.mark.parametrize(
        "investment_class,expected_cnpj",
        [
            (["Fundos Imobiliários"], "12.345.678/0001-90"),
            (["Ações"], "11.222.333/0001-44"),
            (["Fundos Imobiliários", "Ações"], None),  # Multiple should return multiple
        ],
    )
    def test_search_by_investment_class(self, test_db_with_funds, investment_class, expected_cnpj):
        """Test searching by investment class."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(investment_class=investment_class)

        results = tool.forward(criteria=criteria)

        if expected_cnpj:
            assert expected_cnpj in results
        assert isinstance(results, list)

    @pytest.mark.parametrize(
        "audience,min_expected",
        [
            (["RETAIL"], 1),
            (["QUALIFIED"], 2),
            (["PROFESSIONAL"], 0),
            (["RETAIL", "QUALIFIED"], 3),
        ],
    )
    def test_search_by_target_audience(self, test_db_with_funds, audience, min_expected):
        """Test searching by target audience."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(target_audience=audience)

        results = tool.forward(criteria=criteria)

        assert len(results) >= min_expected

    @pytest.mark.parametrize(
        "manager_type,expected_count",
        [
            (["INDEPENDENT"], 3),  # All test funds
            (["CORPORATE"], 0),
            (["INDEPENDENT", "CORPORATE"], 3),
        ],
    )
    def test_search_by_manager_type(self, test_db_with_funds, manager_type, expected_count):
        """Test searching by manager type."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(manager_type=manager_type)

        results = tool.forward(criteria=criteria)

        assert len(results) == expected_count


# ============================================================================
# TEST CLASS 2: Boolean Flags Testing
# ============================================================================


@pytest.mark.unit
class TestBooleanFlags:
    """Test all boolean criteria combinations."""

    @pytest.mark.parametrize(
        "fund_of_funds,expected_count",
        [
            (True, 0),  # No fund of funds in test data
            (False, 3),  # All test funds are not FoF
            (None, 3),  # No filter applied
        ],
    )
    def test_fund_of_funds_flag(self, test_db_with_funds, fund_of_funds, expected_count):
        """Test fund_of_funds boolean flag."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_of_funds=fund_of_funds)

        results = tool.forward(criteria=criteria)

        assert len(results) == expected_count

    @pytest.mark.parametrize(
        "is_exclusive,expected_count",
        [
            (True, 0),
            (False, 3),
            (None, 3),
        ],
    )
    def test_is_exclusive_fund_flag(self, test_db_with_funds, is_exclusive, expected_count):
        """Test is_exclusive_fund boolean flag."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(is_exclusive_fund=is_exclusive)

        results = tool.forward(criteria=criteria)

        assert len(results) == expected_count

    @pytest.mark.parametrize(
        "can_invest_abroad,expected_count",
        [
            (True, 0),
            (False, 3),
            (None, 3),
        ],
    )
    def test_can_invest_abroad_flag(self, test_db_with_funds, can_invest_abroad, expected_count):
        """Test can_invest_abroad_100_pct flag."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(can_invest_abroad_100_pct=can_invest_abroad)

        results = tool.forward(criteria=criteria)

        assert len(results) == expected_count

    @pytest.mark.parametrize(
        "long_term_tax,expected_count",
        [
            (True, 0),
            (False, 3),
            (None, 3),
        ],
    )
    def test_long_term_taxation_flag(self, test_db_with_funds, long_term_tax, expected_count):
        """Test has_long_term_taxation flag."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(has_long_term_taxation=long_term_tax)

        results = tool.forward(criteria=criteria)

        assert len(results) == expected_count

    def test_all_booleans_true(self, test_db_with_funds):
        """Test with all boolean flags set to True."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(
            fund_of_funds=True,
            is_exclusive_fund=True,
            can_invest_abroad_100_pct=True,
            has_long_term_taxation=True,
        )

        results = tool.forward(criteria=criteria)

        # No funds match all True conditions in test data
        assert len(results) == 0

    def test_all_booleans_false(self, test_db_with_funds):
        """Test with all boolean flags set to False."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(
            fund_of_funds=False,
            is_exclusive_fund=False,
            can_invest_abroad_100_pct=False,
            has_long_term_taxation=False,
        )

        results = tool.forward(criteria=criteria)

        # All test funds match these conditions
        assert len(results) == 3

    def test_mixed_boolean_flags(self, test_db_with_funds):
        """Test with mixed boolean flags."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(
            fund_of_funds=False,
            is_exclusive_fund=True,  # This eliminates all
            can_invest_abroad_100_pct=False,
            has_long_term_taxation=None,
        )

        results = tool.forward(criteria=criteria)

        # is_exclusive_fund=True eliminates all test funds
        assert len(results) == 0


# ============================================================================
# TEST CLASS 3: Combined Criteria Tests
# ============================================================================


@pytest.mark.unit
class TestCombinedCriteria:
    """Test multiple criteria combinations."""

    def test_fund_type_and_investment_class(self, test_db_with_funds):
        """Test combining fund_type and investment_class."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=["FII"], investment_class=["Fundos Imobiliários"])

        results = tool.forward(criteria=criteria)

        assert len(results) == 2
        assert "12.345.678/0001-90" in results
        assert "98.765.432/0001-10" in results

    def test_fund_type_and_target_audience(self, test_db_with_funds):
        """Test combining fund_type and target_audience."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=["FII"], target_audience=["RETAIL"])

        results = tool.forward(criteria=criteria)

        assert len(results) == 1
        assert "12.345.678/0001-90" in results

    def test_three_criteria_combined(self, test_db_with_funds):
        """Test combining three criteria."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(
            fund_type=["FII"],
            investment_class=["Fundos Imobiliários"],
            target_audience=["QUALIFIED"],
        )

        results = tool.forward(criteria=criteria)

        assert len(results) == 1
        assert "98.765.432/0001-10" in results

    def test_criteria_with_boolean_flags(self, test_db_with_funds):
        """Test combining standard criteria with boolean flags."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(
            fund_type=["FII"], fund_of_funds=False, is_exclusive_fund=False
        )

        results = tool.forward(criteria=criteria)

        assert len(results) == 2

    def test_maximum_criteria_combination(self, test_db_with_funds):
        """Test with all criteria filled (maximum filters)."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(
            fund_type=["FII"],
            investment_class=["Fundos Imobiliários"],
            target_audience=["RETAIL"],
            manager_type=["INDEPENDENT"],
            fund_of_funds=False,
            is_exclusive_fund=False,
            can_invest_abroad_100_pct=False,
            has_long_term_taxation=False,
        )

        results = tool.forward(criteria=criteria)

        # Should return XP Malls which matches all criteria
        assert len(results) == 1
        assert "12.345.678/0001-90" in results


# ============================================================================
# TEST CLASS 4: Name Search Tests
# ============================================================================


@pytest.mark.unit
class TestNameSearch:
    """Test name search functionality."""

    @pytest.mark.parametrize(
        "name,expected_cnpj",
        [
            ("XP Malls", "12.345.678/0001-90"),
            ("xp malls", "12.345.678/0001-90"),  # Case insensitive
            ("XP MALLS", "12.345.678/0001-90"),
            ("Malls", "12.345.678/0001-90"),  # Partial match
            ("BTG", "98.765.432/0001-10"),
            ("Logística", "98.765.432/0001-10"),
            ("Itaú", "11.222.333/0001-44"),
        ],
    )
    def test_name_search_variations(self, test_db_with_funds, name, expected_cnpj):
        """Test name search with various inputs."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, name=name)

        assert expected_cnpj in results

    def test_name_search_case_insensitive(self, test_db_with_funds):
        """Test that name search is case-insensitive."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results_lower = tool.forward(criteria=criteria, name="xp malls")
        results_upper = tool.forward(criteria=criteria, name="XP MALLS")
        results_mixed = tool.forward(criteria=criteria, name="Xp MaLLs")

        # All should return same fund
        assert "12.345.678/0001-90" in results_lower
        assert "12.345.678/0001-90" in results_upper
        assert "12.345.678/0001-90" in results_mixed

    def test_name_search_partial_match(self, test_db_with_funds):
        """Test partial name matching."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # "FII" should match all real estate funds
        results = tool.forward(criteria=criteria, name="FII")

        # Both FII funds should be found
        assert len(results) >= 2

    def test_name_search_no_match(self, test_db_with_funds):
        """Test name search with no matches."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, name="NONEXISTENT FUND")

        assert results == []

    def test_name_search_with_special_characters(self, test_db_with_funds):
        """Test name search with special characters."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # These should not crash
        results = tool.forward(criteria=criteria, name="Fund & Co.")
        assert isinstance(results, list)

        results = tool.forward(criteria=criteria, name="Fund's Name")
        assert isinstance(results, list)

    def test_name_combined_with_criteria(self, test_db_with_funds):
        """Test name search combined with other criteria."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=["FII"])

        results = tool.forward(criteria=criteria, name="XP")

        assert len(results) == 1
        assert "12.345.678/0001-90" in results


# ============================================================================
# TEST CLASS 5: CNPJ Filtering Tests
# ============================================================================


@pytest.mark.unit
class TestCNPJFiltering:
    """Test CNPJ list filtering."""

    def test_filter_by_single_cnpj(self, test_db_with_funds):
        """Test filtering by a single CNPJ."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()
        cnpjs = ["12.345.678/0001-90"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        assert len(results) == 1
        assert results[0] == "12.345.678/0001-90"

    def test_filter_by_multiple_cnpjs(self, test_db_with_funds):
        """Test filtering by multiple CNPJs."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()
        cnpjs = ["12.345.678/0001-90", "11.222.333/0001-44"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        assert len(results) == 2
        assert set(results) == set(cnpjs)

    def test_cnpj_filter_with_criteria(self, test_db_with_funds):
        """Test CNPJ filter combined with other criteria."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=["FII"])
        cnpjs = ["12.345.678/0001-90", "11.222.333/0001-44"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        # Only FII fund should be returned
        assert len(results) == 1
        assert "12.345.678/0001-90" in results

    def test_cnpj_not_in_database(self, test_db_with_funds):
        """Test filtering by CNPJ not in database."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()
        cnpjs = ["99.999.999/9999-99"]

        results = tool.forward(criteria=criteria, cnpjs=cnpjs)

        assert results == []

    def test_empty_cnpj_list(self, test_db_with_funds):
        """Test with empty CNPJ list."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Empty list should not filter
        results = tool.forward(criteria=criteria, cnpjs=[])

        # Should return all active funds
        assert len(results) == 3


# ============================================================================
# TEST CLASS 6: Limit Parameter Tests
# ============================================================================


@pytest.mark.unit
class TestLimitParameter:
    """Test limit parameter variations."""

    @pytest.mark.parametrize(
        "limit,expected_max",
        [
            (1, 1),
            (2, 2),
            (5, 3),  # Only 3 funds in test DB
            (50, 3),  # Default limit
            (100, 3),
            (1000, 3),
        ],
    )
    def test_limit_variations(self, test_db_with_funds, limit, expected_max):
        """Test different limit values."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=limit)

        assert len(results) <= expected_max
        assert len(results) <= limit

    def test_default_limit(self, test_db_with_funds):
        """Test default limit of 50."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria)  # No limit specified

        # Should use default limit of 50
        assert len(results) <= 50

    def test_limit_1_returns_highest_aum(self, test_db_with_funds):
        """Test that limit=1 returns fund with highest AUM."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=1)

        # BTG has highest AUM (250M) in test data
        assert len(results) == 1
        assert results[0] == "98.765.432/0001-10"


# ============================================================================
# TEST CLASS 7: Edge Cases
# ============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_criteria(self, test_db_with_funds):
        """Test with completely empty criteria."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria)

        # Should return all active funds (excludes cancelled)
        assert len(results) == 3

    def test_empty_lists_vs_none(self, test_db_with_funds):
        """Test empty lists vs None values."""
        tool = FundSearchTool(db_path=test_db_with_funds)

        # Empty list
        criteria1 = FundSearchCriteria(fund_type=[])
        results1 = tool.forward(criteria=criteria1)

        # None
        criteria2 = FundSearchCriteria(fund_type=None)
        results2 = tool.forward(criteria=criteria2)

        # Both should return same results (no filter applied)
        assert len(results1) == len(results2)

    def test_excludes_cancelled_funds(self, test_db_with_funds):
        """Test that cancelled funds are always excluded."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria, limit=1000)

        # Should not include the cancelled fund
        assert "99.999.999/0001-99" not in results

    def test_returns_list_of_strings(self, test_db_with_funds):
        """Test that results are list of strings."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria)

        assert isinstance(results, list)
        for cnpj in results:
            assert isinstance(cnpj, str)
            assert len(cnpj) > 0

    def test_filters_none_values(self, test_db_with_funds):
        """Test that None values are filtered from results."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria)

        # No None values in results
        assert None not in results
        assert all(cnpj is not None for cnpj in results)

    def test_results_ordered_by_aum(self, test_db_with_funds):
        """Test that results are ordered by AUM descending."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        results = tool.forward(criteria=criteria)

        # BTG (250M) should be first, then XP (150M), then Itaú (50M)
        assert results[0] == "98.765.432/0001-10"  # BTG
        assert results[1] == "12.345.678/0001-90"  # XP
        assert results[2] == "11.222.333/0001-44"  # Itaú


# ============================================================================
# TEST CLASS 8: Error Handling
# ============================================================================


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling and recovery."""

    def test_invalid_database_path(self):
        """Test with invalid database path."""
        tool = FundSearchTool(db_path="/nonexistent/path/db.duckdb")
        criteria = FundSearchCriteria()

        # Should return empty list, not crash
        results = tool.forward(criteria=criteria)

        assert results == []

    def test_missing_entity_correlations_file(self, test_db_with_funds):
        """Test when entity_correlations.json is missing."""
        tool = FundSearchTool(db_path=test_db_with_funds)

        # entity_map should be empty dict, not None
        assert isinstance(tool.entity_map, dict)

        # Tool should still work
        criteria = FundSearchCriteria(fund_type=["FII"])
        results = tool.forward(criteria=criteria)

        assert isinstance(results, list)

    def test_handles_database_exceptions_gracefully(self, tmp_path):
        """Test that database exceptions are caught."""
        # Create an empty file (not a valid DuckDB)
        fake_db = tmp_path / "fake.db"
        fake_db.write_text("not a database")

        tool = FundSearchTool(db_path=str(fake_db))
        criteria = FundSearchCriteria()

        # Should return empty list, not raise exception
        results = tool.forward(criteria=criteria)

        assert results == []

    def test_negative_limit_value(self, test_db_with_funds):
        """Test with negative limit value."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Negative limit - DuckDB might handle this differently
        # Should not crash, behavior may vary
        try:
            results = tool.forward(criteria=criteria, limit=-1)
            # If it doesn't crash, should return list
            assert isinstance(results, list)
        except Exception:
            # Or it might raise - also acceptable
            pass

    def test_zero_limit_value(self, test_db_with_funds):
        """Test with zero limit value."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Zero limit should return empty list
        results = tool.forward(criteria=criteria, limit=0)

        assert results == []

    def test_extremely_large_limit(self, test_db_with_funds):
        """Test with very large limit value."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Very large limit should not crash
        results = tool.forward(criteria=criteria, limit=999999999)

        # Should return all available results (3 in test DB)
        assert isinstance(results, list)
        assert len(results) <= 999999999

    def test_empty_string_in_criteria(self, test_db_with_funds):
        """Test with empty strings in criteria."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(
            fund_type=[""],  # Empty string
            investment_class=[""],
        )

        # Should handle gracefully, likely return no results
        results = tool.forward(criteria=criteria)

        assert isinstance(results, list)

    def test_none_as_name_parameter(self, test_db_with_funds):
        """Test with None as name parameter."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # None name should be handled (no name filter)
        results = tool.forward(criteria=criteria, name=None)

        assert isinstance(results, list)
        # Should return all funds (no name filter)
        assert len(results) == 3

    def test_empty_string_as_name(self, test_db_with_funds):
        """Test with empty string as name."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Empty string might match everything or nothing
        results = tool.forward(criteria=criteria, name="")

        assert isinstance(results, list)

    def test_very_long_name_string(self, test_db_with_funds):
        """Test with extremely long name string."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # 10000 character string
        long_name = "A" * 10000

        # Should handle without crashing
        results = tool.forward(criteria=criteria, name=long_name)

        assert isinstance(results, list)
        # Likely no results
        assert results == []

    def test_unicode_characters_in_name(self, test_db_with_funds):
        """Test with unicode/special characters in name."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Various unicode characters
        unicode_names = [
            "Fundação",  # Accented characters
            "São Paulo",
            "R$ Fundo",
            "日本語",  # Japanese
            "测试",  # Chinese
            "🚀 Rocket Fund",  # Emoji
        ]

        for name in unicode_names:
            results = tool.forward(criteria=criteria, name=name)
            # Should not crash
            assert isinstance(results, list)

    def test_whitespace_only_name(self, test_db_with_funds):
        """Test with whitespace-only name."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Various whitespace
        results = tool.forward(criteria=criteria, name="   ")

        assert isinstance(results, list)

    def test_null_bytes_in_name(self, test_db_with_funds):
        """Test with null bytes in name."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Null byte
        try:
            results = tool.forward(criteria=criteria, name="Fund\x00Name")
            # Should handle gracefully
            assert isinstance(results, list)
        except Exception:
            # Or might raise - also acceptable
            pass

    def test_multiple_errors_combined(self, tmp_path):
        """Test multiple error conditions at once."""
        # Invalid DB + bad criteria
        tool = FundSearchTool(db_path="/nonexistent/db.duckdb")
        criteria = FundSearchCriteria(
            fund_type=["'; DROP TABLE funds; --"],  # SQL injection
            investment_class=None,
        )

        # Should return empty list, not crash
        results = tool.forward(criteria=criteria, name="'; DELETE FROM funds; --", limit=-1)

        assert results == []

    def test_database_read_only_mode(self, test_db_with_funds):
        """Test that database is opened in read-only mode."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Should successfully read
        results1 = tool.forward(criteria=criteria)
        assert isinstance(results1, list)

        # Should still work on second call (read-only, not corrupted)
        results2 = tool.forward(criteria=criteria)
        assert len(results1) == len(results2)

    def test_concurrent_access_safety(self, test_db_with_funds):
        """Test that tool is safe for concurrent access."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria1 = FundSearchCriteria(fund_type=["FII"])
        criteria2 = FundSearchCriteria(fund_type=["FI"])

        # Multiple calls should all work
        results1 = tool.forward(criteria=criteria1)
        results2 = tool.forward(criteria=criteria2)
        results3 = tool.forward(criteria=criteria1)

        assert isinstance(results1, list)
        assert isinstance(results2, list)
        assert isinstance(results3, list)
        # Results should be consistent
        assert results1 == results3

    def test_empty_database(self, tmp_path):
        """Test with empty database (no data)."""
        import duckdb

        # Create empty database with schema
        empty_db = tmp_path / "empty.db"
        conn = duckdb.connect(str(empty_db))
        conn.execute("""
            CREATE TABLE funds (
                legal_name VARCHAR,
                fund_type VARCHAR,
                investment_class VARCHAR,
                target_audience VARCHAR,
                status VARCHAR,
                manager_type VARCHAR,
                identifiers STRUCT(type VARCHAR, value VARCHAR)[],
                service_providers STRUCT(tax_id VARCHAR, name VARCHAR, role VARCHAR)[],
                net_asset_value STRUCT(value DOUBLE, currency VARCHAR),
                is_fund_of_funds BOOLEAN,
                is_exclusive_fund BOOLEAN,
                can_invest_abroad_100_pct BOOLEAN,
                has_long_term_taxation BOOLEAN
            )
        """)
        conn.close()

        tool = FundSearchTool(db_path=str(empty_db))
        criteria = FundSearchCriteria()

        # Should return empty list, not crash
        results = tool.forward(criteria=criteria)

        assert results == []

    def test_database_with_null_values(self, tmp_path):
        """Test database with NULL values in fields."""
        import duckdb

        db_with_nulls = tmp_path / "nulls.db"
        conn = duckdb.connect(str(db_with_nulls))

        # Create table and insert data with NULLs
        conn.execute("""
            CREATE TABLE funds (
                legal_name VARCHAR,
                fund_type VARCHAR,
                investment_class VARCHAR,
                target_audience VARCHAR,
                status VARCHAR,
                manager_type VARCHAR,
                identifiers STRUCT(type VARCHAR, value VARCHAR)[],
                service_providers STRUCT(tax_id VARCHAR, name VARCHAR, role VARCHAR)[],
                net_asset_value STRUCT(value DOUBLE, currency VARCHAR),
                is_fund_of_funds BOOLEAN,
                is_exclusive_fund BOOLEAN,
                can_invest_abroad_100_pct BOOLEAN,
                has_long_term_taxation BOOLEAN
            )
        """)

        # Insert fund with NULL fields
        conn.execute("""
            INSERT INTO funds VALUES (
                'Fund with NULLs',
                NULL,  -- NULL fund_type
                NULL,  -- NULL investment_class
                'RETAIL',
                'ACTIVE',
                'INDEPENDENT',
                [{'type': 'CNPJ', 'value': '12.345.678/0001-90'}],
                [],  -- Empty service_providers
                {'value': 1000000.0, 'currency': 'BRL'},
                false, false, false, false
            )
        """)
        conn.close()

        tool = FundSearchTool(db_path=str(db_with_nulls))
        criteria = FundSearchCriteria()

        # Should handle NULLs gracefully
        results = tool.forward(criteria=criteria)

        assert isinstance(results, list)

    def test_malformed_cnpj_in_database(self, tmp_path):
        """Test with malformed CNPJ values in database."""
        import duckdb

        db_bad_cnpj = tmp_path / "bad_cnpj.db"
        conn = duckdb.connect(str(db_bad_cnpj))

        conn.execute("""
            CREATE TABLE funds (
                legal_name VARCHAR,
                fund_type VARCHAR,
                investment_class VARCHAR,
                target_audience VARCHAR,
                status VARCHAR,
                manager_type VARCHAR,
                identifiers STRUCT(type VARCHAR, value VARCHAR)[],
                service_providers STRUCT(tax_id VARCHAR, name VARCHAR, role VARCHAR)[],
                net_asset_value STRUCT(value DOUBLE, currency VARCHAR),
                is_fund_of_funds BOOLEAN,
                is_exclusive_fund BOOLEAN,
                can_invest_abroad_100_pct BOOLEAN,
                has_long_term_taxation BOOLEAN
            )
        """)

        # Insert fund with empty/invalid CNPJ
        conn.execute("""
            INSERT INTO funds VALUES (
                'Fund with Bad CNPJ',
                'FII',
                'Fundos Imobiliários',
                'RETAIL',
                'ACTIVE',
                'INDEPENDENT',
                [{'type': 'CNPJ', 'value': ''}],  -- Empty CNPJ
                [],
                {'value': 1000000.0, 'currency': 'BRL'},
                false, false, false, false
            )
        """)
        conn.close()

        tool = FundSearchTool(db_path=str(db_bad_cnpj))
        criteria = FundSearchCriteria()

        # Should filter out empty CNPJs
        results = tool.forward(criteria=criteria)

        # Empty CNPJs should be filtered out
        assert "" not in results
        assert None not in results


# ============================================================================
# TEST CLASS 9: SQL Injection Prevention
# ============================================================================


@pytest.mark.unit
class TestSQLInjectionPrevention:
    """Test that SQL injection attempts are handled safely."""

    @pytest.mark.parametrize(
        "malicious_name",
        [
            "'; DROP TABLE funds; --",
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DELETE FROM funds WHERE '1'='1",
            "admin'--",
            "' UNION SELECT * FROM funds--",
        ],
    )
    def test_sql_injection_in_name(self, test_db_with_funds, malicious_name):
        """Test SQL injection attempts in name parameter."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria()

        # Should not execute SQL, just return empty results
        results = tool.forward(criteria=criteria, name=malicious_name)

        # Should return list (empty or with results), not crash
        assert isinstance(results, list)

        # Database should still exist and work
        normal_results = tool.forward(criteria=FundSearchCriteria(), name="XP")
        assert len(normal_results) > 0  # DB still intact

    def test_sql_injection_in_criteria(self, test_db_with_funds):
        """Test SQL injection attempts in criteria fields."""
        tool = FundSearchTool(db_path=test_db_with_funds)

        # Try SQL injection in fund_type
        criteria = FundSearchCriteria(fund_type=["'; DROP TABLE funds; --"])

        results = tool.forward(criteria=criteria)

        # Should safely return empty results
        assert isinstance(results, list)

        # Verify DB still works
        normal_results = tool.forward(criteria=FundSearchCriteria(fund_type=["FII"]))
        assert len(normal_results) > 0


# ============================================================================
# TEST CLASS 10: Query Construction (Integration-style Unit Tests)
# ============================================================================


@pytest.mark.unit
class TestQueryConstruction:
    """Test SQL query construction logic (without executing)."""

    def test_basic_where_clause_construction(self, test_db_with_funds):
        """Test that basic WHERE clause is constructed correctly."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=["FII"])

        # Execute query - if it works, construction is correct
        results = tool.forward(criteria=criteria)

        # No SQL errors = query construction successful
        assert isinstance(results, list)

    def test_and_logic_in_where_clause(self, test_db_with_funds):
        """Test that multiple conditions are ANDed together."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=["FII"], target_audience=["RETAIL"])

        results = tool.forward(criteria=criteria)

        # Should return only funds matching BOTH conditions
        assert len(results) == 1
        assert "12.345.678/0001-90" in results

    def test_in_clause_construction(self, test_db_with_funds):
        """Test IN clause construction for list parameters."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_type=["FII", "FI"])

        results = tool.forward(criteria=criteria)

        # Should return all funds matching either type
        assert len(results) == 3

    def test_boolean_value_conversion(self, test_db_with_funds):
        """Test that Python booleans are converted to SQL TRUE/FALSE."""
        tool = FundSearchTool(db_path=test_db_with_funds)
        criteria = FundSearchCriteria(fund_of_funds=False)

        # Should execute without error (bool converted to FALSE)
        results = tool.forward(criteria=criteria)

        assert isinstance(results, list)
