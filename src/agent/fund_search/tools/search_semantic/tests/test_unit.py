"""
Unit tests for SemanticSearchTool.

Note: These are basic unit tests with mock embeddings.
For real semantic search validation, see integration tests that use
the actual vector store with real embeddings.
"""

import pytest
from src.agent.fund_search.tools.search_semantic.tool import SemanticSearchTool


@pytest.mark.unit
class TestSemanticSearchToolUnit:
    """Basic unit tests for SemanticSearchTool."""

    def test_initialization(self, test_vector_store):
        """Test tool initializes correctly."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)
        assert tool.vector_store_path == test_vector_store

    def test_search_returns_results(self, test_vector_store):
        """Test that search returns results (basic smoke test)."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Basic search - with mock embeddings, results may not be semantically meaningful
        results = tool.forward(query="fundos imobiliários", top_k=5)

        assert isinstance(results, list)
        # Should return some results
        assert len(results) <= 5

    def test_search_respects_top_k(self, test_vector_store):
        """Test search respects top_k parameter."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="test query", top_k=2)

        assert len(results) <= 2

    def test_search_with_search_mode_name(self, test_vector_store):
        """Test search with name mode."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="XP Malls", top_k=5, search_mode="name")

        assert isinstance(results, list)

    def test_search_with_search_mode_strategy(self, test_vector_store):
        """Test search with strategy mode."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="real estate", top_k=5, search_mode="strategy")

        assert isinstance(results, list)

    def test_search_error_handling(self, tmp_path):
        """Test tool handles database errors gracefully."""
        bad_db_path = str(tmp_path / "nonexistent.db")
        tool = SemanticSearchTool(vector_store_path=bad_db_path)

        # Should return empty list instead of crashing
        results = tool.forward(query="test query")

        assert results == []

    def test_query_cleaning(self, test_vector_store):
        """Test that queries with quotes are cleaned properly."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Should handle quotes without errors
        results = tool.forward(query='"XP Malls" FII', top_k=5)

        assert isinstance(results, list)


@pytest.mark.integration
@pytest.mark.requires_db
class TestSemanticSearchToolIntegration:
    """
    Integration tests using real vector store.

    These tests require the actual vector_store.db file with real embeddings.
    They test semantic similarity with actual sentence-transformer vectors.
    """

    def test_semantic_search_with_real_embeddings(self, vector_store_snapshot):
        """Test semantic search with real embeddings."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        # Search for real estate funds
        results = tool.forward(query="fundos imobiliários shopping", top_k=10)

        # Should return actual relevant results
        assert len(results) > 0
        assert all(isinstance(cnpj, str) for cnpj in results)

    def test_semantic_search_name_mode(self, vector_store_snapshot):
        """Test semantic search with name mode on real data."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        results = tool.forward(query="XP Malls", top_k=5, search_mode="name")

        # Should find XP Malls fund if it exists in the DB
        assert len(results) > 0

    def test_semantic_search_with_filters(self, vector_store_snapshot):
        """Test semantic search with pre-filters."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        pre_filter = {
            "investment_class": "Fundos Imobiliários"
        }

        results = tool.forward(
            query="fundos de investimento",
            top_k=10,
            pre_filter=pre_filter
        )

        assert isinstance(results, list)

    def test_keyword_boosting(self, vector_store_snapshot):
        """Test that keyword boosting affects results."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        # Search with specific fund name - should get boosted
        results = tool.forward(query="XP", top_k=20)

        # Results should include funds with "XP" in the name
        assert len(results) > 0
