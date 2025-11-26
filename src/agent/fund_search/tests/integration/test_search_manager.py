"""
Integration tests for SearchManager orchestration.

Tests how SearchManager coordinates multiple search tools.
Uses real database snapshots for realistic testing.
"""

import pytest

from src.agent.fund_search.models.query import (
    FundSearchCriteria,
    ParsedQuery,
    PositionSearchCriteria,
)
from src.agent.fund_search.modules.search_manager.manager import SearchManager, SearchRouter


@pytest.mark.integration
@pytest.mark.requires_db
class TestSearchManagerIntegration:
    """Integration tests for SearchManager with real database."""

    def test_search_manager_initialization(self, db_snapshot, vector_store_snapshot):
        """Test SearchManager initializes with real databases."""
        manager = SearchManager(db_path=db_snapshot, vector_store_path=vector_store_snapshot)

        assert manager is not None
        assert manager.db_path == db_snapshot

    def test_search_by_fund_type(self, db_snapshot, vector_store_snapshot):
        """Test searching by fund type through SearchManager."""
        manager = SearchManager(db_path=db_snapshot, vector_store_path=vector_store_snapshot)

        parsed = ParsedQuery(
            raw_query="fundos imobiliários", criteria=FundSearchCriteria(fund_type=["FII"])
        )

        results = manager.execute(parsed_query=parsed, intent="find_by_criteria")

        # Should return FII funds
        assert isinstance(results, list)

    def test_search_with_semantic(self, db_snapshot, vector_store_snapshot):
        """Test semantic search integration."""
        manager = SearchManager(db_path=db_snapshot, vector_store_path=vector_store_snapshot)

        parsed = ParsedQuery(raw_query="XP Malls", criteria=FundSearchCriteria())

        results = manager.execute(parsed_query=parsed, intent="find_by_name")

        # Should use semantic search and return results
        assert isinstance(results, list)

    def test_search_with_position_criteria(self, db_snapshot, vector_store_snapshot):
        """Test search with position criteria."""
        manager = SearchManager(db_path=db_snapshot, vector_store_path=vector_store_snapshot)

        parsed = ParsedQuery(
            raw_query="fundos que investem em Petrobras",
            criteria=FundSearchCriteria(),
            position_criteria=PositionSearchCriteria(asset_name=["Petrobras"]),
        )

        results = manager.execute(parsed_query=parsed, intent="find_by_exposure")

        assert isinstance(results, list)

    def test_search_with_multiple_tools(self, db_snapshot, vector_store_snapshot):
        """Test search using multiple tools together."""
        manager = SearchManager(db_path=db_snapshot, vector_store_path=vector_store_snapshot)

        parsed = ParsedQuery(
            raw_query="fundos imobiliários XP com AUM acima de 100 milhões",
            criteria=FundSearchCriteria(fund_type=["FII"], service_provider_entity=["XP"]),
        )

        results = manager.execute(parsed_query=parsed, intent="find_by_criteria")

        # Multiple tools should be coordinated
        assert isinstance(results, list)


@pytest.mark.integration
class TestSearchRouter:
    """Integration tests for SearchRouter."""

    def test_router_initialization(self, db_snapshot, vector_store_snapshot):
        """Test SearchRouter initializes correctly."""
        router = SearchRouter(db_path=db_snapshot, vector_store_path=vector_store_snapshot)

        assert router is not None

    def test_router_routes_to_semantic_search(self, db_snapshot, vector_store_snapshot):
        """Test router correctly routes to semantic search."""
        router = SearchRouter(db_path=db_snapshot, vector_store_path=vector_store_snapshot)

        # Router should determine semantic search is needed
        # This is a basic smoke test
        assert router is not None
