"""Fixtures for search_positions tool tests."""

import pytest
import duckdb


@pytest.fixture
def test_db_with_positions(tmp_path):
    """Create a test database with sample position data."""
    db_path = tmp_path / "test_positions.db"
    conn = duckdb.connect(str(db_path))

    # Create fund_positions table
    conn.execute("""
        CREATE TABLE fund_positions (
            cnpj VARCHAR,
            asset_name VARCHAR,
            ticker VARCHAR,
            asset_type VARCHAR,
            position_value DOUBLE,
            quantity DOUBLE
        )
    """)

    # Insert sample positions
    conn.execute("""
        INSERT INTO fund_positions VALUES
        ('12.345.678/0001-90', 'Petrobras PN', 'PETR4', 'Equity', 500000.0, 10000),
        ('12.345.678/0001-90', 'Vale ON', 'VALE3', 'Equity', 300000.0, 5000),
        ('98.765.432/0001-10', 'Petrobras PN', 'PETR4', 'Equity', 1000000.0, 20000),
        ('98.765.432/0001-10', 'Itaú Unibanco PN', 'ITUB4', 'Equity', 750000.0, 15000),
        ('11.222.333/0001-44', 'Vale ON', 'VALE3', 'Equity', 200000.0, 3000),
        ('11.222.333/0001-44', 'B3 ON', 'B3SA3', 'Equity', 150000.0, 2000)
    """)

    conn.close()
    return str(db_path)
