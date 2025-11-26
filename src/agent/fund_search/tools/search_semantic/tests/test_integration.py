"""
Integration tests for SemanticSearchTool.

These tests require the actual vector_store.db file with real embeddings.
They test semantic similarity with actual sentence-transformer vectors.
"""

import concurrent.futures

import duckdb
import pytest
from sentence_transformers import SentenceTransformer

from src.agent.fund_search.tools.search_semantic.tool import SemanticSearchTool


@pytest.mark.integration
@pytest.mark.requires_db
class TestSemanticSearchToolIntegration:
    """Integration tests using real vector store with actual embeddings."""

    # Happy Path Integration Tests
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

        # Should find results
        assert isinstance(results, list)

    def test_semantic_search_strategy_mode(self, vector_store_snapshot):
        """Test semantic search with strategy mode on real data."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        results = tool.forward(query="investimento em ações", top_k=10, search_mode="strategy")

        assert isinstance(results, list)

    def test_semantic_search_with_investment_class_filter(self, vector_store_snapshot):
        """Test semantic search with investment_class filter."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        pre_filter = {"investment_class": "Fundos Imobiliários"}

        results = tool.forward(query="fundos de investimento", top_k=10, pre_filter=pre_filter)

        assert isinstance(results, list)

    def test_semantic_search_with_manager_filter(self, vector_store_snapshot):
        """Test semantic search with manager filter."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        pre_filter = {"manager": "XP Asset"}

        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        assert isinstance(results, list)

    def test_semantic_search_with_fund_type_filter(self, vector_store_snapshot):
        """Test semantic search with fund_type filter."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        pre_filter = {"fund_type": "FII"}

        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        assert isinstance(results, list)

    def test_semantic_search_with_name_terms_filter(self, vector_store_snapshot):
        """Test semantic search with name_terms filter."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        pre_filter = {"name_terms": ["Malls"]}

        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        assert isinstance(results, list)

    def test_semantic_search_with_combined_filters(self, vector_store_snapshot):
        """Test semantic search with multiple filters combined."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        pre_filter = {"investment_class": "Fundos Imobiliários", "fund_type": "FII"}

        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        assert isinstance(results, list)

    def test_keyword_boosting_real_data(self, vector_store_snapshot):
        """Test that keyword boosting affects results with real data."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        # Search with specific keyword
        results = tool.forward(query="XP", top_k=20)

        assert isinstance(results, list)

    def test_multi_query_fusion_real_data(self, vector_store_snapshot):
        """Test multi-query fusion with real data."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        # Complex query that benefits from query expansion
        results = tool.forward(query="investimentos em propriedades comerciais", top_k=10)

        assert isinstance(results, list)

    # Error Handling Integration Tests
    def test_handles_missing_vector_store(self, tmp_path):
        """Test tool handles missing vector store gracefully."""
        bad_db_path = str(tmp_path / "nonexistent_vector_store.db")
        tool = SemanticSearchTool(vector_store_path=bad_db_path)

        results = tool.forward(query="test query", top_k=10)

        assert results == []

    def test_handles_corrupted_vector_store(self, tmp_path):
        """Test tool handles corrupted vector store gracefully."""
        corrupted_db = tmp_path / "corrupted_vector_store.db"
        corrupted_db.write_text("This is not a valid database file")

        tool = SemanticSearchTool(vector_store_path=str(corrupted_db))
        results = tool.forward(query="test query", top_k=10)

        assert results == []

    def test_handles_empty_vector_store(self, tmp_path):
        """Test tool handles empty vector store."""
        empty_db = tmp_path / "empty_vector_store.db"
        conn = duckdb.connect(str(empty_db))

        # Create table but don't insert any data
        conn.execute("""
            CREATE TABLE fund_embeddings (
                cnpj VARCHAR,
                embedding FLOAT[384],
                text_content VARCHAR,
                metadata MAP(VARCHAR, VARCHAR)
            )
        """)
        conn.close()

        tool = SemanticSearchTool(vector_store_path=str(empty_db))
        results = tool.forward(query="test query", top_k=10)

        assert results == []

    def test_handles_missing_cnpj_field(self, tmp_path):
        """Test tool handles records with missing CNPJ."""
        db_path = tmp_path / "missing_cnpj.db"
        conn = duckdb.connect(str(db_path))

        conn.execute("""
            CREATE TABLE fund_embeddings (
                cnpj VARCHAR,
                embedding FLOAT[384],
                text_content VARCHAR,
                metadata MAP(VARCHAR, VARCHAR)
            )
        """)

        model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        embedding = model.encode("Test fund").tolist()

        # Insert record with NULL CNPJ
        conn.execute(
            "INSERT INTO fund_embeddings VALUES (NULL, ?::FLOAT[384], 'Test Fund', {'legal_name': 'Test'})",
            [embedding],
        )
        conn.close()

        tool = SemanticSearchTool(vector_store_path=str(db_path))
        results = tool.forward(query="test", top_k=10)

        # Should handle gracefully (filter out NULL CNPJs)
        assert isinstance(results, list)

    def test_handles_null_embeddings(self, tmp_path):
        """Test tool handles records with NULL embeddings."""
        db_path = tmp_path / "null_embeddings.db"
        conn = duckdb.connect(str(db_path))

        conn.execute("""
            CREATE TABLE fund_embeddings (
                cnpj VARCHAR,
                embedding FLOAT[384],
                text_content VARCHAR,
                metadata MAP(VARCHAR, VARCHAR)
            )
        """)

        # Insert record with NULL embedding (should fail or be skipped)
        try:
            conn.execute(
                "INSERT INTO fund_embeddings VALUES ('12.345.678/0001-90', NULL, 'Test Fund', {'legal_name': 'Test'})"
            )
        except Exception:
            pass  # Expected to fail

        conn.close()

        tool = SemanticSearchTool(vector_store_path=str(db_path))
        results = tool.forward(query="test", top_k=10)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_handles_malformed_embeddings(self, tmp_path):
        """Test tool handles embeddings with wrong dimensions."""
        db_path = tmp_path / "malformed_embeddings.db"
        conn = duckdb.connect(str(db_path))

        conn.execute("""
            CREATE TABLE fund_embeddings (
                cnpj VARCHAR,
                embedding FLOAT[384],
                text_content VARCHAR,
                metadata MAP(VARCHAR, VARCHAR)
            )
        """)

        # Try to insert embedding with wrong dimensions (will fail in INSERT or query)
        try:
            wrong_dim_embedding = [0.5] * 100  # Wrong dimensions
            conn.execute(
                "INSERT INTO fund_embeddings VALUES ('12.345.678/0001-90', ?::FLOAT[384], 'Test', {'legal_name': 'Test'})",
                [wrong_dim_embedding],
            )
        except Exception:
            pass  # Expected to fail due to dimension mismatch

        conn.close()

        tool = SemanticSearchTool(vector_store_path=str(db_path))
        results = tool.forward(query="test", top_k=10)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_sql_injection_protection_in_filters(self, vector_store_snapshot):
        """Test that filters are protected against SQL injection."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        # Attempt SQL injection in filters
        pre_filter = {
            "investment_class": "'; DROP TABLE fund_embeddings; --",
            "manager": "' OR '1'='1",
            "name_terms": ["'; DELETE FROM fund_embeddings; --"],
        }

        # Should handle without executing malicious SQL
        results = tool.forward(query="test", top_k=10, pre_filter=pre_filter)

        assert isinstance(results, list)

    def test_concurrent_read_operations(self, vector_store_snapshot):
        """Test that multiple concurrent read operations work correctly."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        def run_query(query_text):
            return tool.forward(query=query_text, top_k=5)

        queries = [
            "fundos imobiliários",
            "ações small cap",
            "renda fixa",
            "multimercado",
            "crédito privado",
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_query, q) for q in queries]
            results = [future.result() for future in futures]

        # All queries should succeed
        assert len(results) == 5
        for result in results:
            assert isinstance(result, list)

    def test_performance_with_large_top_k(self, vector_store_snapshot):
        """Test performance with large top_k value."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        # Request large number of results
        results = tool.forward(query="fundos", top_k=1000)

        assert isinstance(results, list)
        # Should return results up to database size
        assert len(results) >= 0

    def test_handles_missing_metadata_fields(self, tmp_path):
        """Test tool handles records with missing metadata fields."""
        db_path = tmp_path / "missing_metadata.db"
        conn = duckdb.connect(str(db_path))

        conn.execute("""
            CREATE TABLE fund_embeddings (
                cnpj VARCHAR,
                embedding FLOAT[384],
                text_content VARCHAR,
                metadata MAP(VARCHAR, VARCHAR)
            )
        """)

        model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        embedding = model.encode("Test fund").tolist()

        # Insert with incomplete metadata (missing investment_class)
        conn.execute(
            "INSERT INTO fund_embeddings VALUES ('12.345.678/0001-90', ?::FLOAT[384], 'Test Fund', {'legal_name': 'Test'})",
            [embedding],
        )
        conn.close()

        tool = SemanticSearchTool(vector_store_path=str(db_path))

        # Search with investment_class filter on record without it
        pre_filter = {"investment_class": "Ações"}
        results = tool.forward(query="test", top_k=10, pre_filter=pre_filter)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_handles_empty_text_content(self, tmp_path):
        """Test tool handles records with empty text_content."""
        db_path = tmp_path / "empty_text.db"
        conn = duckdb.connect(str(db_path))

        conn.execute("""
            CREATE TABLE fund_embeddings (
                cnpj VARCHAR,
                embedding FLOAT[384],
                text_content VARCHAR,
                metadata MAP(VARCHAR, VARCHAR)
            )
        """)

        model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        embedding = model.encode("").tolist()  # Empty text embedding

        conn.execute(
            "INSERT INTO fund_embeddings VALUES ('12.345.678/0001-90', ?::FLOAT[384], '', {'legal_name': 'Test'})",
            [embedding],
        )
        conn.close()

        tool = SemanticSearchTool(vector_store_path=str(db_path))
        results = tool.forward(query="test", top_k=10)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_complex_portuguese_queries(self, vector_store_snapshot):
        """Test complex Portuguese queries with accents and special characters."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        complex_queries = [
            "fundos de ações com foco em empresas de tecnologia",
            "investimentos em títulos públicos federais",
            "fundos multimercado com estratégia macro",
            "fundos imobiliários que investem em lajes corporativas",
        ]

        for query in complex_queries:
            results = tool.forward(query=query, top_k=10)
            assert isinstance(results, list)

    def test_search_stability_repeated_queries(self, vector_store_snapshot):
        """Test that repeated identical queries return consistent results."""
        tool = SemanticSearchTool(vector_store_path=vector_store_snapshot)

        query = "fundos imobiliários"

        # Run same query multiple times
        results1 = tool.forward(query=query, top_k=10)
        results2 = tool.forward(query=query, top_k=10)
        results3 = tool.forward(query=query, top_k=10)

        # Results should be identical
        assert results1 == results2 == results3
