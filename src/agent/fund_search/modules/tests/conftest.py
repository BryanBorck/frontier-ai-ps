"""Fixtures for module tests."""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_dspy_predict():
    """
    Mock DSPy Predict module for testing intent classification and extraction.
    """
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_intent_response():
    """Sample intent classification response."""
    mock = Mock()
    mock.intent = "find_by_criteria"
    mock.confidence = 0.95
    mock.reasoning = "User is searching for funds by investment criteria"
    return mock


@pytest.fixture
def sample_extraction_response():
    """Sample extraction response."""
    from src.agent.fund_search.models.query import FundSearchCriteria

    mock = Mock()
    mock.criteria = FundSearchCriteria(
        fund_type=["FII"],
        investment_class=["Fundos Imobiliários"]
    )
    mock.confidence = 0.9
    return mock


@pytest.fixture
def sample_queries():
    """Sample user queries for testing."""
    return {
        "find_by_name": "Encontre o fundo XP Malls",
        "find_by_criteria": "Fundos de ações para investidores qualificados",
        "find_by_exposure": "Fundos que investem em Petrobras",
        "numeric_filter": "Fundos com AUM acima de 100 milhões",
        "informational": "O que é um FII?",
        "followup": "Quero ver apenas os de renda fixa"
    }
