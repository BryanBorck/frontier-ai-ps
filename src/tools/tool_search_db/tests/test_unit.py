"""Unit tests for tool_search_db."""

import pytest

from src.tools.tool_parse_query.module_pipeline import FundSearchCriteria
from src.tools.tool_search_db.index import tool_search_db
from src.tools.tool_search_db.module_pipeline import FundResult, search_funds


class TestSearchFunds:
    """Test search_funds function."""

    def test_search_by_fund_type_fip(self):
        """Test searching for FIP funds."""
        criteria = FundSearchCriteria(fund_type="FIP")
        results = search_funds(criteria, limit=5)

        assert isinstance(results, list)
        assert len(results) <= 5
        assert len(results) > 0

        for fund in results:
            assert isinstance(fund, FundResult)
            assert fund.fund_type == "FIP"

    def test_search_by_fund_type_fidc(self):
        """Test searching for FIDC funds."""
        criteria = FundSearchCriteria(fund_type="FIDC")
        results = search_funds(criteria, limit=5)

        assert len(results) > 0
        for fund in results:
            assert fund.fund_type == "FIDC"

    def test_search_by_fund_name(self):
        """Test searching by fund legal name."""
        criteria = FundSearchCriteria(fund_legal_name="Vinci")
        results = search_funds(criteria, limit=5)

        assert len(results) > 0
        for fund in results:
            assert "vinci" in fund.legal_name.lower()

    def test_search_with_limit(self):
        """Test that limit parameter works."""
        criteria = FundSearchCriteria(fund_type="FIP")
        results = search_funds(criteria, limit=3)

        assert len(results) <= 3

    def test_search_no_results(self):
        """Test search that returns no results."""
        criteria = FundSearchCriteria(fund_legal_name="XYZNONEXISTENT123")
        results = search_funds(criteria)

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_multiple_criteria(self):
        """Test search with multiple criteria."""
        criteria = FundSearchCriteria(fund_type="FIP", investment_class="FIP")
        results = search_funds(criteria, limit=5)

        assert isinstance(results, list)
        for fund in results:
            assert fund.fund_type == "FIP"

    def test_result_structure(self):
        """Test that results have expected structure."""
        criteria = FundSearchCriteria(fund_type="FIP")
        results = search_funds(criteria, limit=1)

        assert len(results) > 0
        fund = results[0]

        assert isinstance(fund, FundResult)
        assert fund.legal_name is not None
        assert fund.cnpj is not None
        assert hasattr(fund, "fund_type")
        assert hasattr(fund, "investment_class")


class TestToolSearchDB:
    """Test tool_search_db function."""

    def test_tool_search_db_success(self):
        """Test tool_search_db with valid input."""
        result = tool_search_db(
            {"criteria": {"fund_type": "FIP"}, "limit": 5}
        )

        assert isinstance(result, list)
        assert len(result) <= 5
        assert len(result) > 0

        for fund in result:
            assert isinstance(fund, dict)
            assert "legal_name" in fund
            assert "cnpj" in fund
            assert "fund_type" in fund
            assert "investment_class" in fund

    def test_tool_search_db_missing_criteria(self):
        """Test tool_search_db with missing criteria field."""
        with pytest.raises(ValueError, match="Missing required field 'criteria'"):
            tool_search_db({})

    def test_tool_search_db_returns_list(self):
        """Test tool_search_db returns list of dicts."""
        result = tool_search_db({"criteria": {"fund_type": "FIP"}})
        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], dict)

    def test_tool_search_db_with_limit(self):
        """Test tool_search_db respects limit parameter."""
        result = tool_search_db(
            {"criteria": {"fund_type": "FIP"}, "limit": 2}
        )
        assert len(result) <= 2

    def test_tool_search_db_no_results(self):
        """Test tool_search_db with no matching results."""
        result = tool_search_db(
            {"criteria": {"fund_legal_name": "XYZNONEXISTENT123"}}
        )
        assert isinstance(result, list)
        assert len(result) == 0
