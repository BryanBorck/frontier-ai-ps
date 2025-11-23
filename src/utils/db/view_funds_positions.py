"""View sample rows from funds and positions tables."""

import duckdb
import pandas as pd


def view_funds_and_positions(db_path: str = "docs/br_funds.db", num_rows: int = 10):
    """Display first N rows from funds and positions tables.

    Args:
        db_path: Path to the DuckDB database file
        num_rows: Number of rows to display per table
    """
    conn = duckdb.connect(db_path, read_only=True)

    for table_name in ["funds", "positions"]:
        print("\n" + "=" * 120)
        print(f"TABLE: {table_name}")
        print("=" * 120)

        # Get row count
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Total rows: {count:,}")
        print(f"Showing first {num_rows} rows:\n")

        # Fetch sample data
        df = conn.execute(f"SELECT * FROM {table_name} LIMIT {num_rows}").fetchdf()

        # Show each row in detail
        for idx in range(len(df)):
            print(f"\n{'─' * 120}")
            print(f"Row {idx + 1} of {num_rows}")
            print(f"{'─' * 120}")
            for col in df.columns:
                value = df.iloc[idx][col]
                value_str = str(value)
                if len(value_str) > 150:
                    value_str = value_str[:150] + "..."
                print(f"  {col:30s}: {value_str}")

        print("\n")

    conn.close()


if __name__ == "__main__":
    view_funds_and_positions()
