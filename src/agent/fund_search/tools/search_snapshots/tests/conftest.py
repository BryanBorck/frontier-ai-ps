"""Fixtures for search_snapshots tool tests."""

import pytest
import duckdb


@pytest.fixture
def test_db_with_snapshots(tmp_path):
    """Create a test database with sample snapshot data."""
    db_path = tmp_path / "test_snapshots.db"
    conn = duckdb.connect(str(db_path))

    # Create fund_snapshots table
    conn.execute("""
        CREATE TABLE fund_snapshots (
            cnpj VARCHAR,
            net_assets_value STRUCT(value DOUBLE, date DATE),
            number_of_holders STRUCT(value INTEGER, date DATE)
        )
    """)

    # Insert sample snapshots
    conn.execute("""
        INSERT INTO fund_snapshots VALUES
        (
            '12.345.678/0001-90',
            {'value': 150000000.0, 'date': '2024-01-31'},
            {'value': 5000, 'date': '2024-01-31'}
        ),
        (
            '98.765.432/0001-10',
            {'value': 250000000.0, 'date': '2024-01-31'},
            {'value': 3000, 'date': '2024-01-31'}
        ),
        (
            '11.222.333/0001-44',
            {'value': 50000000.0, 'date': '2024-01-31'},
            {'value': 1200, 'date': '2024-01-31'}
        ),
        (
            '22.333.444/0001-55',
            {'value': 500000.0, 'date': '2024-01-31'},
            {'value': 50, 'date': '2024-01-31'}
        )
    """)

    conn.close()
    return str(db_path)
