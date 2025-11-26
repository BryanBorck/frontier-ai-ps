"""Fixtures for search_semantic tool tests."""

import os
import shutil

import duckdb
import numpy as np
import pytest
from sentence_transformers import SentenceTransformer


@pytest.fixture(scope="session")
def real_vector_store_path():
    """Path to the real vector store database."""
    return "src/infrastructure/database/vector_store.db"


@pytest.fixture
def vector_store_snapshot(tmp_path, real_vector_store_path):
    """Create a temporary copy of the real vector store for integration tests."""
    if not os.path.exists(real_vector_store_path):
        pytest.skip(f"Real vector store not found at {real_vector_store_path}")

    snapshot = tmp_path / "snapshot_vector_store.db"
    shutil.copy(real_vector_store_path, snapshot)
    return str(snapshot)


@pytest.fixture
def test_vector_store(tmp_path):
    """
    Create a comprehensive test vector store for unit testing.

    Uses actual sentence-transformer embeddings for realistic semantic search testing.
    Includes diverse fund types, investment classes, and metadata for thorough testing.
    """
    db_path = tmp_path / "test_vector_store.db"
    conn = duckdb.connect(str(db_path))

    # Create fund_embeddings table matching production schema
    conn.execute("""
        CREATE TABLE fund_embeddings (
            cnpj VARCHAR,
            embedding FLOAT[384],
            text_content VARCHAR,
            metadata MAP(VARCHAR, VARCHAR)
        )
    """)

    # Use actual sentence transformer for realistic embeddings
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    # Define comprehensive test fund data with diverse characteristics
    test_funds = [
        {
            "cnpj": "12.345.678/0001-90",
            "text": "Fund Name: XP Malls FII | Type: FII Investment Class: Fundos Imobiliários Manager: XP Asset Management Benchmark: IFIX Risk Profile: Medium Strategy Description: Investe em shoppings centers de alto padrão Investment Policy: Foco em shopping centers classe A",
            "legal_name": "XP Malls FII",
            "investment_class": "Fundos Imobiliários",
        },
        {
            "cnpj": "98.765.432/0001-10",
            "text": "Fund Name: BTG Pactual Logística FII | Type: FII Investment Class: Fundos Imobiliários Manager: BTG Pactual Asset Management Benchmark: IFIX Risk Profile: Medium-High Strategy Description: Foco em galpões logísticos e centros de distribuição Investment Policy: Investimentos em ativos logísticos de última geração",
            "legal_name": "BTG Pactual Logística FII",
            "investment_class": "Fundos Imobiliários",
        },
        {
            "cnpj": "11.222.333/0001-44",
            "text": "Fund Name: Itaú Ações Small Cap FI | Type: FI Investment Class: Ações Manager: Itaú Asset Management Benchmark: SMLL Risk Profile: High Strategy Description: Investe em ações de empresas de pequena capitalização Investment Policy: Foco em small caps com potencial de crescimento",
            "legal_name": "Itaú Ações Small Cap FI",
            "investment_class": "Ações",
        },
        {
            "cnpj": "22.333.444/0001-55",
            "text": "Fund Name: Bradesco Renda Fixa Referenciado DI FI | Type: FI Investment Class: Renda Fixa Manager: Bradesco Asset Management Benchmark: CDI Risk Profile: Low Strategy Description: Acompanha a variação do CDI Investment Policy: Investe em títulos públicos e privados de renda fixa",
            "legal_name": "Bradesco Renda Fixa Referenciado DI FI",
            "investment_class": "Renda Fixa",
        },
        {
            "cnpj": "33.444.555/0001-66",
            "text": "Fund Name: Santander Multimercado Macro FIC FIM | Type: FIM Investment Class: Multimercado Manager: Santander Asset Management Benchmark: CDI Risk Profile: High Strategy Description: Estratégia macro global com alocação em diversos mercados Investment Policy: Investe em renda fixa, ações, câmbio e derivativos",
            "legal_name": "Santander Multimercado Macro FIC FIM",
            "investment_class": "Multimercado",
        },
        {
            "cnpj": "44.555.666/0001-77",
            "text": "Fund Name: XP Crédito Privado FI | Type: FI Investment Class: Renda Fixa Manager: XP Asset Management Benchmark: CDI Risk Profile: Medium-High Strategy Description: Investe em crédito privado de emissores de alta qualidade Investment Policy: Foco em debêntures e CRIs de empresas sólidas",
            "legal_name": "XP Crédito Privado FI",
            "investment_class": "Renda Fixa",
        },
        {
            "cnpj": "55.666.777/0001-88",
            "text": "Fund Name: Verde Asset Allocation FIC FIM | Type: FIM Investment Class: Multimercado Manager: Verde Asset Management Benchmark: IPCA+6% Risk Profile: High Strategy Description: Long-biased equity com foco em value investing Investment Policy: Carteira concentrada em ações com desconto em relação ao valor intrínseco",
            "legal_name": "Verde Asset Allocation FIC FIM",
            "investment_class": "Multimercado",
        },
        {
            "cnpj": "66.777.888/0001-99",
            "text": "Fund Name: Kinea Infraestrutura FIP | Type: FIP Investment Class: Fundos de Investimento em Participações Manager: Kinea Investimentos Benchmark: IPCA+8% Risk Profile: High Strategy Description: Investe em infraestrutura e energia renovável Investment Policy: Foco em projetos de energia solar, eólica e transmissão",
            "legal_name": "Kinea Infraestrutura FIP",
            "investment_class": "Fundos de Investimento em Participações",
        },
    ]

    # Generate embeddings for all test funds
    texts = [fund["text"] for fund in test_funds]
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Insert all test data
    for fund, embedding in zip(test_funds, embeddings):
        conn.execute(
            """
            INSERT INTO fund_embeddings VALUES (?, ?::FLOAT[384], ?, ?)
        """,
            [
                fund["cnpj"],
                embedding.tolist(),
                fund["text"],
                {"legal_name": fund["legal_name"], "investment_class": fund["investment_class"]},
            ],
        )

    conn.close()
    return str(db_path)
