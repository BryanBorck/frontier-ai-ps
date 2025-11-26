"""
Shared test fixtures for fund_search integration and E2E tests.

This conftest provides fixtures used across integration and E2E tests,
including database mocks, LLM mocks, and common test data.
"""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures" / "data"


@pytest.fixture(scope="session")
def real_db_path():
    """
    Path to the real production database.
    Used for integration and E2E tests that need real data.
    """
    return "src/infrastructure/database/br_funds.db"


@pytest.fixture(scope="session")
def real_vector_store_path():
    """
    Path to the real vector store database.
    Critical for semantic search tests with actual embeddings.
    """
    return "src/infrastructure/database/vector_store.db"


@pytest.fixture
def db_snapshot(tmp_path, real_db_path):
    """
    Create a temporary copy of the real database.
    Use this for integration tests that need real data but shouldn't modify it.

    Benefits:
    - Real schema and data
    - No risk of corrupting production DB
    - Each test gets a fresh copy
    """
    import os

    if not os.path.exists(real_db_path):
        pytest.skip(f"Real database not found at {real_db_path}")

    snapshot = tmp_path / "snapshot_br_funds.db"
    shutil.copy(real_db_path, snapshot)
    return str(snapshot)


@pytest.fixture
def vector_store_snapshot(tmp_path, real_vector_store_path):
    """
    Create a temporary copy of the real vector store.
    Essential for semantic search integration tests.
    """
    import os

    if not os.path.exists(real_vector_store_path):
        pytest.skip(f"Real vector store not found at {real_vector_store_path}")

    snapshot = tmp_path / "snapshot_vector_store.db"
    shutil.copy(real_vector_store_path, snapshot)
    return str(snapshot)


@pytest.fixture
def mock_db_path(tmp_path):
    """
    Create a simple mock DuckDB database for unit testing.
    Use this for fast unit tests that don't need real data.

    For integration tests, use db_snapshot instead.
    """
    from src.agent.fund_search.tests.fixtures.db_fixtures import create_test_db

    db_path = tmp_path / "test_funds.db"
    create_test_db(str(db_path))
    return str(db_path)


@pytest.fixture
def mock_vector_store_path(tmp_path):
    """
    Create a simple mock vector store for unit testing.
    For semantic search integration tests, use vector_store_snapshot instead.
    """
    vector_db_path = tmp_path / "test_vector_store.db"
    # TODO: Initialize with minimal test embeddings if needed
    return str(vector_db_path)


@pytest.fixture
def sample_fund_results():
    """
    Sample fund search results for testing.
    Returns a list of mock fund results.
    """
    return [
        {
            "cnpj": "12.345.678/0001-90",
            "fund_name": "XP Malls FII",
            "fund_type": "FII",
            "investment_class": "Renda Fixa",
            "target_audience": "RETAIL",
        },
        {
            "cnpj": "98.765.432/0001-10",
            "fund_name": "BTG Pactual Logística FII",
            "fund_type": "FII",
            "investment_class": "Fundos Imobiliários",
            "target_audience": "QUALIFIED",
        },
    ]


@pytest.fixture
def sample_cnpjs():
    """Sample CNPJs for testing."""
    return ["12.345.678/0001-90", "98.765.432/0001-10", "11.222.333/0001-44"]


@pytest.fixture
def mock_llm_response():
    """
    Mock LLM response for DSPy signature testing.
    Returns a mock that simulates DSPy completion.
    """
    mock = MagicMock()
    mock.intent = "find_by_criteria"
    mock.confidence = 0.95
    return mock


@pytest.fixture
def mock_intent_classifier():
    """
    Mock IntentClassifier for testing without LLM calls.
    """
    mock = Mock()
    mock.classify.return_value = Mock(intent="find_by_criteria", confidence=0.95)
    return mock


@pytest.fixture
def mock_specialized_extractor():
    """
    Mock SpecializedExtractor for testing without LLM calls.
    """
    from src.agent.fund_search.models.query import FundSearchCriteria, ParsedQuery

    mock = Mock()
    mock.extract.return_value = ParsedQuery(
        raw_query="fundos de ações", criteria=FundSearchCriteria(investment_class=["Ações"])
    )
    return mock


@pytest.fixture
def mock_conversation_state():
    """
    Mock ConversationState for multi-turn testing.
    """
    from src.agent.fund_search.models.query import FundSearchCriteria
    from src.agent.fund_search.models.state import ConversationState

    return ConversationState(
        turn=1,
        accumulated_criteria=FundSearchCriteria(),
        last_cnpjs=[],
        history=[],
        awaiting_clarification=False,
    )


@pytest.fixture
def mock_tracing_manager():
    """
    Mock TracingManager to avoid MLflow calls during tests.
    """
    mock = Mock()
    mock.start_trace.return_value = Mock()
    mock.log_event.return_value = None
    mock.end_trace.return_value = None
    return mock


@pytest.fixture(autouse=True)
def disable_mlflow(monkeypatch):
    """
    Automatically disable MLflow tracing in all tests.
    """
    monkeypatch.setenv("MLFLOW_ENABLED", "false")


@pytest.fixture
def sample_user_queries():
    """
    Sample user queries for testing various intent types.
    """
    return {
        "find_by_name": "Encontre o fundo XP Malls",
        "find_by_criteria": "Fundos de ações para investidores qualificados",
        "find_by_exposure": "Fundos que investem em Petrobras",
        "numeric_filter": "Fundos com AUM acima de 100 milhões",
        "informational": "O que é um FII?",
        "followup": "Quero ver apenas os de renda fixa",
    }
