"""Quick script to explore the DuckDB database."""

import duckdb


def explore_database(db_path: str = "docs/br_funds.db"):
    """Explore and display information about the DuckDB database.

    Args:
        db_path: Path to the DuckDB database file
    """
    # Connect to the database
    conn = duckdb.connect(db_path, read_only=True)

    # Show all tables
    print("=" * 80)
    print("TABLES IN DATABASE:")
    print("=" * 80)
    tables = conn.execute("SHOW TABLES").fetchall()
    for table in tables:
        print(f"  - {table[0]}")

    print("\n" + "=" * 80)
    print("TABLE SCHEMAS:")
    print("=" * 80)

    # For each table, show schema and sample data
    for table_name in [t[0] for t in tables]:
        print(f"\n📊 Table: {table_name}")
        print("-" * 80)

        # Get schema
        schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
        print("\nColumns:")
        for col in schema:
            print(f"  • {col[0]}: {col[1]}")

        # Get row count
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"\nTotal rows: {count:,}")

        # Show sample data (first 3 rows)
        print(f"\nSample data (first 3 rows):")
        sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchdf()
        print(sample.to_string())
        print("\n")

    conn.close()


if __name__ == "__main__":
    explore_database()
