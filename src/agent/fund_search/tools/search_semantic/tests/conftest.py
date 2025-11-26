"""Fixtures for search_semantic tool tests."""

import pytest
import duckdb
import numpy as np


@pytest.fixture
def test_vector_store(tmp_path):
    """
    Create a minimal test vector store for unit testing.

    Note: For real semantic search testing, use vector_store_snapshot
    from the root conftest (integration tests).
    """
    db_path = tmp_path / "test_vector_store.db"
    conn = duckdb.connect(str(db_path))

    # Create fund_embeddings table
    conn.execute("""
        CREATE TABLE fund_embeddings (
            cnpj VARCHAR,
            embedding FLOAT[384],
            text_content VARCHAR,
            metadata MAP(VARCHAR, VARCHAR)
        )
    """)

    # Create simple test embeddings (normalized random vectors)
    # In real tests, we'd use actual sentence-transformer embeddings
    def random_embedding():
        vec = np.random.randn(384)
        return (vec / np.linalg.norm(vec)).tolist()

    # Insert sample data
    conn.execute("""
        INSERT INTO fund_embeddings VALUES
        (
            '12.345.678/0001-90',
            ?::FLOAT[384],
            'Fund Name: XP Malls FII Type: FII Investment Class: Fundos Imobiliários',
            {'legal_name': 'XP Malls FII', 'investment_class': 'Fundos Imobiliários'}
        ),
        (
            '98.765.432/0001-10',
            ?::FLOAT[384],
            'Fund Name: BTG Pactual Logística FII Type: FII Investment Class: Fundos Imobiliários',
            {'legal_name': 'BTG Pactual Logística FII', 'investment_class': 'Fundos Imobiliários'}
        ),
        (
            '11.222.333/0001-44',
            ?::FLOAT[384],
            'Fund Name: Itaú Ações Small Cap FI Type: FI Investment Class: Ações',
            {'legal_name': 'Itaú Ações Small Cap FI', 'investment_class': 'Ações'}
        )
    """, [random_embedding(), random_embedding(), random_embedding()])

    conn.close()
    return str(db_path)
