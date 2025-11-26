"""Fixtures for search_performance tool tests."""

import os
import shutil
from datetime import datetime, timedelta

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
def test_db_with_performance(tmp_path):
    """Create a test database with sample performance data matching real schema."""
    db_path = tmp_path / "test_performance.db"
    conn = duckdb.connect(str(db_path))

    # Create funds table (needed for the join) - matching real schema
    conn.execute("""
        CREATE TABLE funds (
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            identifiers STRUCT(type VARCHAR, value VARCHAR)[]
        )
    """)

    # Create fund_performance_indicators table - matching real schema
    conn.execute("""
        CREATE TABLE fund_performance_indicators (
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            first_date VARCHAR,
            return_pct DOUBLE
        )
    """)

    # Insert sample funds
    conn.execute("""
        INSERT INTO funds VALUES
        (
            {'type': 'CVM', 'value': 'FUND001'},
            [{'type': 'CNPJ', 'value': '12.345.678/0001-90'}]
        ),
        (
            {'type': 'CVM', 'value': 'FUND002'},
            [{'type': 'CNPJ', 'value': '98.765.432/0001-10'}]
        ),
        (
            {'type': 'CVM', 'value': 'FUND003'},
            [{'type': 'CNPJ', 'value': '11.222.333/0001-44'}]
        ),
        (
            {'type': 'CVM', 'value': 'FUND004'},
            [{'type': 'CNPJ', 'value': '22.333.444/0001-55'}]
        )
    """)

    # Insert sample performance data (recent dates)
    recent_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    older_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    very_old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")

    conn.execute(f"""
        INSERT INTO fund_performance_indicators VALUES
        -- FUND001: Total 23.5% return (high performer)
        ({{'type': 'CVM', 'value': 'FUND001'}}, '{recent_date}', 15.5),
        ({{'type': 'CVM', 'value': 'FUND001'}}, '{older_date}', 8.0),
        -- FUND002: Total 8.5% return (low performer)
        ({{'type': 'CVM', 'value': 'FUND002'}}, '{recent_date}', 5.5),
        ({{'type': 'CVM', 'value': 'FUND002'}}, '{older_date}', 3.0),
        -- FUND003: Total 18.0% return (medium performer)
        ({{'type': 'CVM', 'value': 'FUND003'}}, '{recent_date}', 12.0),
        ({{'type': 'CVM', 'value': 'FUND003'}}, '{older_date}', 6.0),
        -- FUND004: Has old data (should be filtered out for recent periods)
        ({{'type': 'CVM', 'value': 'FUND004'}}, '{very_old_date}', 20.0)
    """)

    conn.close()
    return str(db_path)
