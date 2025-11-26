"""Fixtures for search_performance tool tests."""

import pytest
import duckdb
from datetime import datetime, timedelta


@pytest.fixture
def test_db_with_performance(tmp_path):
    """Create a test database with sample performance data."""
    db_path = tmp_path / "test_performance.db"
    conn = duckdb.connect(str(db_path))

    # Create funds table (needed for the join)
    conn.execute("""
        CREATE TABLE funds (
            fund_id STRUCT(value VARCHAR),
            identifiers STRUCT(type VARCHAR, value VARCHAR)[]
        )
    """)

    # Create fund_performance_indicators table
    conn.execute("""
        CREATE TABLE fund_performance_indicators (
            fund_id STRUCT(value VARCHAR),
            first_date DATE,
            return_pct DOUBLE
        )
    """)

    # Insert sample funds
    conn.execute("""
        INSERT INTO funds VALUES
        (
            {'value': 'fund-1'},
            [{'type': 'CNPJ', 'value': '12.345.678/0001-90'}]
        ),
        (
            {'value': 'fund-2'},
            [{'type': 'CNPJ', 'value': '98.765.432/0001-10'}]
        ),
        (
            {'value': 'fund-3'},
            [{'type': 'CNPJ', 'value': '11.222.333/0001-44'}]
        )
    """)

    # Insert sample performance data (recent dates)
    recent_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    older_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    conn.execute(f"""
        INSERT INTO fund_performance_indicators VALUES
        ({{'value': 'fund-1'}}, '{recent_date}', 15.5),
        ({{'value': 'fund-1'}}, '{older_date}', 8.0),
        ({{'value': 'fund-2'}}, '{recent_date}', 5.5),
        ({{'value': 'fund-2'}}, '{older_date}', 3.0),
        ({{'value': 'fund-3'}}, '{recent_date}', 12.0),
        ({{'value': 'fund-3'}}, '{older_date}', 6.0)
    """)

    conn.close()
    return str(db_path)
