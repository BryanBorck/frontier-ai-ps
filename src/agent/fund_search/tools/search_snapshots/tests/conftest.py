"""Fixtures for search_snapshots tool tests."""

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
def test_db_with_snapshots(tmp_path):
    """Create a test database with sample snapshot data matching real schema."""
    db_path = tmp_path / "test_snapshots.db"
    conn = duckdb.connect(str(db_path))

    # Create funds table (needed for JOIN to get CNPJ)
    conn.execute("""
        CREATE TABLE funds (
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            identifiers STRUCT(type VARCHAR, value VARCHAR)[]
        )
    """)

    # Create fund_snapshots table matching real schema
    # Note: number_of_holders is DOUBLE (not STRUCT), net_assets_value is STRUCT
    conn.execute("""
        CREATE TABLE fund_snapshots (
            snapshot_id STRUCT(type VARCHAR, value VARCHAR),
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            net_assets_value STRUCT(value DOUBLE, currency VARCHAR),
            number_of_holders DOUBLE,
            timestamp TIMESTAMP
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

    # Insert sample snapshots (multiple snapshots per fund to test latest snapshot logic)
    conn.execute("""
        INSERT INTO fund_snapshots VALUES
        -- FUND001 snapshots (latest has 150M AUM, 5000 holders)
        (
            {'type': 'SNAPSHOT', 'value': 'SNAP001'},
            {'type': 'CVM', 'value': 'FUND001'},
            {'value': 100000000.0, 'currency': 'BRL'},
            4500.0,
            '2024-01-15 00:00:00'
        ),
        (
            {'type': 'SNAPSHOT', 'value': 'SNAP002'},
            {'type': 'CVM', 'value': 'FUND001'},
            {'value': 150000000.0, 'currency': 'BRL'},
            5000.0,
            '2024-01-31 00:00:00'
        ),
        -- FUND002 snapshots (latest has 250M AUM, 3000 holders)
        (
            {'type': 'SNAPSHOT', 'value': 'SNAP003'},
            {'type': 'CVM', 'value': 'FUND002'},
            {'value': 250000000.0, 'currency': 'BRL'},
            3000.0,
            '2024-01-31 00:00:00'
        ),
        -- FUND003 snapshots (latest has 50M AUM, 1200 holders)
        (
            {'type': 'SNAPSHOT', 'value': 'SNAP004'},
            {'type': 'CVM', 'value': 'FUND003'},
            {'value': 50000000.0, 'currency': 'BRL'},
            1200.0,
            '2024-01-31 00:00:00'
        ),
        -- FUND004 snapshots (latest has 500k AUM, 50 holders)
        (
            {'type': 'SNAPSHOT', 'value': 'SNAP005'},
            {'type': 'CVM', 'value': 'FUND004'},
            {'value': 500000.0, 'currency': 'BRL'},
            50.0,
            '2024-01-31 00:00:00'
        )
    """)

    conn.close()
    return str(db_path)
