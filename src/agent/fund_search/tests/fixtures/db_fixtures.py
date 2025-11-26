"""
Database fixtures for testing.

Provides utilities to create and populate test databases with sample data.
"""

import duckdb


def create_test_db(db_path: str) -> None:
    """
    Create a test database with sample fund data matching real schema.

    Note: This is a simplified version for unit tests.
    For integration tests, use db_snapshot fixture which copies the real database.
    Schema matches: src/infrastructure/database/README.md

    Args:
        db_path: Path to the database file to create
    """
    conn = duckdb.connect(db_path)

    # Create funds table matching real schema structure
    conn.execute("""
        CREATE TABLE IF NOT EXISTS funds (
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            legal_name VARCHAR,
            fund_type VARCHAR,
            investment_class VARCHAR,
            target_audience VARCHAR,
            status VARCHAR,
            manager_type VARCHAR,
            identifiers STRUCT(type VARCHAR, value VARCHAR)[],
            service_providers STRUCT(
                tax_id VARCHAR,
                name VARCHAR,
                role VARCHAR
            )[],
            net_asset_value STRUCT(value DOUBLE, currency VARCHAR),
            is_fund_of_funds BOOLEAN,
            is_exclusive_fund BOOLEAN,
            can_invest_abroad_100_pct BOOLEAN,
            has_long_term_taxation BOOLEAN
        )
    """)

    # Insert sample data matching real structure
    conn.execute("""
        INSERT INTO funds VALUES
        (
            {'type': 'INTERNAL_HASH', 'value': 'fund-xp-malls'},
            'XP Malls FII',
            'FII',
            'Fundos Imobiliários',
            'RETAIL',
            'ACTIVE',
            'INDEPENDENT',
            [{'type': 'CNPJ', 'value': '12.345.678/0001-90'}, {'type': 'CVM_CODE', 'value': '123456'}],
            [
                {'tax_id': '11.111.111/0001-11', 'name': 'XP Gestão de Recursos Ltda', 'role': 'MANAGER'},
                {'tax_id': '22.222.222/0001-22', 'name': 'XP Admin S.A.', 'role': 'ADMINISTRATOR'},
                {'tax_id': '33.333.333/0001-33', 'name': 'Banco XP', 'role': 'CUSTODIAN'}
            ],
            {'value': 150000000.0, 'currency': 'BRL'},
            false,
            false,
            false,
            false
        ),
        (
            {'type': 'INTERNAL_HASH', 'value': 'fund-btg-logistica'},
            'BTG Pactual Logística FII',
            'FII',
            'Fundos Imobiliários',
            'QUALIFIED',
            'ACTIVE',
            'INDEPENDENT',
            [{'type': 'CNPJ', 'value': '98.765.432/0001-10'}, {'type': 'CVM_CODE', 'value': '654321'}],
            [
                {'tax_id': '44.444.444/0001-44', 'name': 'BTG Pactual Gestão de Recursos Ltda', 'role': 'MANAGER'},
                {'tax_id': '55.555.555/0001-55', 'name': 'BTG Pactual Serviços Financeiros S.A.', 'role': 'ADMINISTRATOR'},
                {'tax_id': '66.666.666/0001-66', 'name': 'Banco BTG Pactual', 'role': 'CUSTODIAN'}
            ],
            {'value': 250000000.0, 'currency': 'BRL'},
            false,
            false,
            false,
            false
        ),
        (
            {'type': 'INTERNAL_HASH', 'value': 'fund-itau-acoes'},
            'Itaú Ações Small Cap FI',
            'FI',
            'Ações',
            'QUALIFIED',
            'ACTIVE',
            'INDEPENDENT',
            [{'type': 'CNPJ', 'value': '11.222.333/0001-44'}, {'type': 'CVM_CODE', 'value': '111222'}],
            [
                {'tax_id': '77.777.777/0001-77', 'name': 'Itaú Asset Management', 'role': 'MANAGER'},
                {'tax_id': '88.888.888/0001-88', 'name': 'Itaú Unibanco S.A.', 'role': 'ADMINISTRATOR'},
                {'tax_id': '99.999.999/0001-99', 'name': 'Itaú Unibanco S.A.', 'role': 'CUSTODIAN'}
            ],
            {'value': 50000000.0, 'currency': 'BRL'},
            false,
            false,
            false,
            false
        )
    """)

    conn.close()


def create_test_positions_table(db_path: str) -> None:
    """
    Create positions table in test database matching real schema.

    Note: Real table is called 'positions', not 'fund_positions'.
    Schema matches: src/infrastructure/database/README.md

    Args:
        db_path: Path to the database file
    """
    conn = duckdb.connect(db_path)

    # Note: The tool uses 'fund_positions' table name, but real DB has 'positions'
    # Creating both for compatibility with different test scenarios
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fund_positions (
            position_id STRUCT(type VARCHAR, value VARCHAR),
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            asset_id STRUCT(type VARCHAR, value VARCHAR),
            cnpj VARCHAR,
            asset_name VARCHAR,
            ticker VARCHAR,
            asset_type VARCHAR,
            quantity DOUBLE,
            position_value DOUBLE,
            current_market_value STRUCT(value DOUBLE, currency VARCHAR)
        )
    """)

    # Insert sample positions
    conn.execute("""
        INSERT INTO fund_positions VALUES
        (
            {'type': 'INTERNAL_HASH', 'value': 'pos-1'},
            {'type': 'INTERNAL_HASH', 'value': 'fund-itau-acoes'},
            {'type': 'INTERNAL_HASH', 'value': 'asset-petr4'},
            '11.222.333/0001-44',
            'Petrobras PN',
            'PETR4',
            'Equity',
            10000,
            250000,
            {'value': 250000.0, 'currency': 'BRL'}
        ),
        (
            {'type': 'INTERNAL_HASH', 'value': 'pos-2'},
            {'type': 'INTERNAL_HASH', 'value': 'fund-itau-acoes'},
            {'type': 'INTERNAL_HASH', 'value': 'asset-vale3'},
            '11.222.333/0001-44',
            'Vale ON',
            'VALE3',
            'Equity',
            8000,
            180000,
            {'value': 180000.0, 'currency': 'BRL'}
        )
    """)

    conn.close()


def create_test_snapshots_table(db_path: str) -> None:
    """
    Create snapshots table in test database matching real schema.

    Schema matches: src/infrastructure/database/README.md

    Args:
        db_path: Path to the database file
    """
    conn = duckdb.connect(db_path)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS fund_snapshots (
            snapshot_id STRUCT(type VARCHAR, value VARCHAR),
            fund_id STRUCT(type VARCHAR, value VARCHAR),
            cnpj VARCHAR,
            timestamp VARCHAR,
            share_price STRUCT(value DOUBLE, currency VARCHAR),
            total_portfolio_value STRUCT(value DOUBLE, currency VARCHAR),
            net_assets_value STRUCT(value DOUBLE, currency VARCHAR),
            daily_inflow_value STRUCT(value DOUBLE, currency VARCHAR),
            daily_outflow_value STRUCT(value DOUBLE, currency VARCHAR),
            number_of_holders STRUCT(value INTEGER, date DATE)
        )
    """)

    # Insert sample snapshots
    conn.execute("""
        INSERT INTO fund_snapshots VALUES
        (
            {'type': 'INTERNAL_HASH', 'value': 'snap-1'},
            {'type': 'INTERNAL_HASH', 'value': 'fund-xp-malls'},
            '12.345.678/0001-90',
            '2024-01-31',
            {'value': 100.50, 'currency': 'BRL'},
            {'value': 150000000.0, 'currency': 'BRL'},
            {'value': 150000000.0, 'currency': 'BRL'},
            {'value': 1000000.0, 'currency': 'BRL'},
            {'value': 500000.0, 'currency': 'BRL'},
            {'value': 5000, 'date': '2024-01-31'}
        ),
        (
            {'type': 'INTERNAL_HASH', 'value': 'snap-2'},
            {'type': 'INTERNAL_HASH', 'value': 'fund-btg-logistica'},
            '98.765.432/0001-10',
            '2024-01-31',
            {'value': 98.75, 'currency': 'BRL'},
            {'value': 250000000.0, 'currency': 'BRL'},
            {'value': 250000000.0, 'currency': 'BRL'},
            {'value': 2000000.0, 'currency': 'BRL'},
            {'value': 1500000.0, 'currency': 'BRL'},
            {'value': 3000, 'date': '2024-01-31'}
        ),
        (
            {'type': 'INTERNAL_HASH', 'value': 'snap-3'},
            {'type': 'INTERNAL_HASH', 'value': 'fund-itau-acoes'},
            '11.222.333/0001-44',
            '2024-01-31',
            {'value': 15.25, 'currency': 'BRL'},
            {'value': 50000000.0, 'currency': 'BRL'},
            {'value': 50000000.0, 'currency': 'BRL'},
            {'value': 500000.0, 'currency': 'BRL'},
            {'value': 300000.0, 'currency': 'BRL'},
            {'value': 1200, 'date': '2024-01-31'}
        )
    """)

    conn.close()
