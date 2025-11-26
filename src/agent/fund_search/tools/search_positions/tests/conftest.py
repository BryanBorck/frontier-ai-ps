"""Fixtures for search_positions tool tests."""

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
def test_db_with_positions(tmp_path):
    """
    Create a test database with positions, assets, and funds tables.

    Matches the real production schema:
    - positions: Links funds to assets with market values
    - assets: Contains asset details (issuer name, tickers, asset class)
    - funds: Contains fund details (CNPJs, fund IDs)
    """
    db_path = tmp_path / "test_positions.db"
    conn = duckdb.connect(str(db_path))

    # Create funds table (matching production schema)
    conn.execute("""
        CREATE TABLE funds (
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            identifiers STRUCT(type VARCHAR, value VARCHAR)[]
        )
    """)

    # Create assets table (matching production schema)
    conn.execute("""
        CREATE TABLE assets (
            asset_id STRUCT(type VARCHAR, value VARCHAR),
            name VARCHAR,
            short_name VARCHAR,
            issuer STRUCT(issuer_name VARCHAR, issuer_type VARCHAR, issuer_id VARCHAR),
            identifiers STRUCT(type VARCHAR, value VARCHAR)[],
            listing STRUCT(exchange VARCHAR, ticker STRUCT(type VARCHAR, value VARCHAR)),
            asset_class VARCHAR,
            financial_instrument VARCHAR
        )
    """)

    # Create positions table (matching production schema)
    conn.execute("""
        CREATE TABLE positions (
            position_id STRUCT(type VARCHAR, value VARCHAR),
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            asset_id STRUCT(type VARCHAR, value VARCHAR),
            quantity DOUBLE,
            current_market_value STRUCT(value DOUBLE, currency VARCHAR)
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

    # Insert sample assets
    conn.execute("""
        INSERT INTO assets VALUES
        -- ASSET001: Petrobras stock (PETR4)
        (
            {'type': 'INTERNAL_HASH', 'value': 'ASSET001'},
            'PETR4 - PETROBRAS PN',
            'PETR4',
            {'issuer_name': 'PETROBRAS', 'issuer_type': 'CORPORATE', 'issuer_id': 'PETROBRAS001'},
            [{'type': 'TICKER', 'value': 'PETR4'}],
            {'exchange': 'BRASIL_BOLSA_BALCAO', 'ticker': {'type': 'TICKER', 'value': 'PETR4'}},
            'EQUITY',
            'STOCK'
        ),
        -- ASSET002: Vale stock (VALE3)
        (
            {'type': 'INTERNAL_HASH', 'value': 'ASSET002'},
            'VALE3 - VALE ON',
            'VALE3',
            {'issuer_name': 'VALE SA', 'issuer_type': 'CORPORATE', 'issuer_id': 'VALE001'},
            [{'type': 'TICKER', 'value': 'VALE3'}],
            {'exchange': 'BRASIL_BOLSA_BALCAO', 'ticker': {'type': 'TICKER', 'value': 'VALE3'}},
            'EQUITY',
            'STOCK'
        ),
        -- ASSET003: Itaú stock (ITUB4)
        (
            {'type': 'INTERNAL_HASH', 'value': 'ASSET003'},
            'ITUB4 - ITAU UNIBANCO PN',
            'ITUB4',
            {'issuer_name': 'ITAU UNIBANCO HOLDING SA', 'issuer_type': 'CORPORATE', 'issuer_id': 'ITAU001'},
            [{'type': 'TICKER', 'value': 'ITUB4'}],
            {'exchange': 'BRASIL_BOLSA_BALCAO', 'ticker': {'type': 'TICKER', 'value': 'ITUB4'}},
            'EQUITY',
            'STOCK'
        ),
        -- ASSET004: Petrobras option (derivative)
        (
            {'type': 'INTERNAL_HASH', 'value': 'ASSET004'},
            'PETROBRAS CALL OPTION',
            'PETRQ123',
            {'issuer_name': 'PETROBRAS', 'issuer_type': 'CORPORATE', 'issuer_id': 'PETROBRAS001'},
            [{'type': 'TICKER', 'value': 'PETRQ123'}],
            {'exchange': 'BRASIL_BOLSA_BALCAO', 'ticker': {'type': 'TICKER', 'value': 'PETRQ123'}},
            'DERIVATIVES',
            'OPTION'
        ),
        -- ASSET005: Investment fund (no ticker)
        (
            {'type': 'INTERNAL_HASH', 'value': 'ASSET005'},
            'XP FUNDO RENDA FIXA',
            'XP RENDA FIXA',
            {'issuer_name': 'XP ASSET MANAGEMENT', 'issuer_type': 'FUND', 'issuer_id': 'XP001'},
            [],
            NULL,
            'INVESTMENT_FUND',
            'FUND'
        ),
        -- ASSET006: BBAS3 (Banco do Brasil)
        (
            {'type': 'INTERNAL_HASH', 'value': 'ASSET006'},
            'BBAS3 - BANCO DO BRASIL ON',
            'BBAS3',
            {'issuer_name': 'BANCO DO BRASIL SA', 'issuer_type': 'CORPORATE', 'issuer_id': 'BB001'},
            [{'type': 'TICKER', 'value': 'BBAS3'}],
            {'exchange': 'BRASIL_BOLSA_BALCAO', 'ticker': {'type': 'TICKER', 'value': 'BBAS3'}},
            'EQUITY',
            'STOCK'
        )
    """)

    # Insert sample positions
    conn.execute("""
        INSERT INTO positions VALUES
        -- FUND001 positions
        (
            {'type': 'POS', 'value': 'P001'},
            {'type': 'CVM', 'value': 'FUND001'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET001'},  -- Petrobras
            10000.0,
            {'value': 500000.0, 'currency': 'BRL'}
        ),
        (
            {'type': 'POS', 'value': 'P002'},
            {'type': 'CVM', 'value': 'FUND001'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET002'},  -- Vale
            5000.0,
            {'value': 300000.0, 'currency': 'BRL'}
        ),
        -- FUND002 positions (high Petrobras exposure)
        (
            {'type': 'POS', 'value': 'P003'},
            {'type': 'CVM', 'value': 'FUND002'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET001'},  -- Petrobras stock
            20000.0,
            {'value': 1000000.0, 'currency': 'BRL'}
        ),
        (
            {'type': 'POS', 'value': 'P004'},
            {'type': 'CVM', 'value': 'FUND002'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET004'},  -- Petrobras option
            100.0,
            {'value': 50000.0, 'currency': 'BRL'}
        ),
        (
            {'type': 'POS', 'value': 'P005'},
            {'type': 'CVM', 'value': 'FUND002'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET003'},  -- Itau
            15000.0,
            {'value': 750000.0, 'currency': 'BRL'}
        ),
        -- FUND003 positions
        (
            {'type': 'POS', 'value': 'P006'},
            {'type': 'CVM', 'value': 'FUND003'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET002'},  -- Vale
            3000.0,
            {'value': 200000.0, 'currency': 'BRL'}
        ),
        (
            {'type': 'POS', 'value': 'P007'},
            {'type': 'CVM', 'value': 'FUND003'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET006'},  -- BB
            2000.0,
            {'value': 150000.0, 'currency': 'BRL'}
        ),
        -- FUND004 positions (fund of funds)
        (
            {'type': 'POS', 'value': 'P008'},
            {'type': 'CVM', 'value': 'FUND004'},
            {'type': 'INTERNAL_HASH', 'value': 'ASSET005'},  -- Investment fund
            10000.0,
            {'value': 1000000.0, 'currency': 'BRL'}
        )
    """)

    conn.close()
    return str(db_path)
