"""Fixtures for search_funds tool tests."""

import os
import shutil

import duckdb
import pytest


@pytest.fixture(scope="session")
def real_db_path():
    """Path to the real production database."""
    return "src/infrastructure/database/br_funds.db"


@pytest.fixture
def db_snapshot(tmp_path, real_db_path):
    """Create a temporary copy of the real database for integration tests."""
    if not os.path.exists(real_db_path):
        pytest.skip(f"Real database not found at {real_db_path}")

    snapshot = tmp_path / "snapshot_br_funds.db"
    shutil.copy(real_db_path, snapshot)
    return str(snapshot)


@pytest.fixture
def test_db_with_funds(tmp_path):
    """Create a test database with sample fund data."""
    db_path = tmp_path / "test_funds.db"
    conn = duckdb.connect(str(db_path))

    # Create funds table matching the expected schema
    conn.execute("""
        CREATE TABLE funds (
            legal_name VARCHAR,
            fund_type VARCHAR,
            investment_class VARCHAR,
            target_audience VARCHAR,
            status VARCHAR,
            manager_type VARCHAR,
            is_fund_of_funds BOOLEAN,
            is_exclusive_fund BOOLEAN,
            can_invest_abroad_100_pct BOOLEAN,
            has_long_term_taxation BOOLEAN,
            identifiers STRUCT(type VARCHAR, value VARCHAR)[],
            service_providers STRUCT(tax_id VARCHAR, name VARCHAR, role VARCHAR)[],
            net_asset_value STRUCT(value DOUBLE, date DATE)
        )
    """)

    # Insert sample data
    conn.execute("""
        INSERT INTO funds VALUES (
            'XP Malls FII',
            'FII',
            'FII',
            'RETAIL',
            'ACTIVE',
            'CORPORATE',
            false,
            false,
            false,
            false,
            [{'type': 'CNPJ', 'value': '12.345.678/0001-90'}],
            [{'tax_id': '11.111.111/0001-11', 'name': 'XP Gestão', 'role': 'MANAGER'}],
            {'value': 150000000.0, 'date': '2024-01-31'}
        ),
        (
            'BTG Pactual Logística FII',
            'FII',
            'FII',
            'QUALIFIED',
            'ACTIVE',
            'CORPORATE',
            false,
            false,
            false,
            false,
            [{'type': 'CNPJ', 'value': '98.765.432/0001-10'}],
            [{'tax_id': '22.222.222/0001-22', 'name': 'BTG Gestão', 'role': 'MANAGER'}],
            {'value': 250000000.0, 'date': '2024-01-31'}
        ),
        (
            'Itaú Ações Small Cap FI',
            'FI',
            'Ações',
            'QUALIFIED',
            'ACTIVE',
            'CORPORATE',
            false,
            false,
            false,
            false,
            [{'type': 'CNPJ', 'value': '11.222.333/0001-44'}],
            [{'tax_id': '33.333.333/0001-33', 'name': 'Itaú Asset', 'role': 'MANAGER'}],
            {'value': 50000000.0, 'date': '2024-01-31'}
        ),
        (
            'Cancelled Fund FI',
            'FI',
            'Renda Fixa',
            'RETAIL',
            'CANCELLED',
            'CORPORATE',
            false,
            false,
            false,
            false,
            [{'type': 'CNPJ', 'value': '99.999.999/0001-99'}],
            [{'tax_id': '44.444.444/0001-44', 'name': 'Test Gestão', 'role': 'MANAGER'}],
            {'value': 10000000.0, 'date': '2024-01-31'}
        )
    """)

    conn.close()
    return str(db_path)
