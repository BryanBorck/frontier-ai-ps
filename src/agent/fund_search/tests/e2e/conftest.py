"""
Fixtures for E2E tests.

E2E tests use the real production database to verify the complete workflow.
"""

import os

import pytest

from src.agent.fund_search.orchestrator import FundSearchTool


@pytest.fixture(scope="session")
def real_db_path():
    """Path to the real production database for E2E tests."""
    return "src/infrastructure/database/br_funds.db"


@pytest.fixture(scope="session")
def real_vector_store_path():
    """Path to the real vector store for E2E tests."""
    return "src/infrastructure/database/vector_store.db"


@pytest.fixture
def api_key():
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set")
    return key


@pytest.fixture
def fund_search_tool(api_key):
    """Create FundSearchTool instance for testing."""
    return FundSearchTool(
        api_key=api_key,
        model="gpt-4o-mini",
        enable_mlflow=False,  # Disable MLflow for tests
    )


# Common test data for ticker mapping
BRAZILIAN_TICKERS = {
    "PETR3": {"company": "Petrobras", "type": "PN"},
    "PETR4": {"company": "Petrobras", "type": "ON"},
    "VALE3": {"company": "Vale", "type": "ON"},
    "ITUB4": {"company": "Itaú", "type": "PN"},
    "BBAS3": {"company": "Banco do Brasil", "type": "ON"},
    "ABEV3": {"company": "Ambev", "type": "ON"},
    "WEGE3": {"company": "WEG", "type": "ON"},
    "B3SA3": {"company": "B3", "type": "ON"},
}


@pytest.fixture
def ticker_mapping():
    """Common ticker-to-company mapping for tests."""
    return BRAZILIAN_TICKERS
