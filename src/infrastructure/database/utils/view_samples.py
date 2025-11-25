"""View sample rows from all tables in the database."""

import duckdb
import pandas as pd


def view_samples(db_path: str = "docs/br_funds.db", num_rows: int = 10):
    """Display first N rows from all tables with all columns.

    Args:
        db_path: Path to the DuckDB database file
        num_rows: Number of rows to display per table
    """
    conn = duckdb.connect(db_path, read_only=True)

    # Configure pandas display options to show all columns
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", 80)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_rows", None)

    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]

    for table_name in table_names:
        print("\n" + "=" * 120)
        print(f"TABLE: {table_name}")
        print("=" * 120)

        # Get row count
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Total rows: {count:,}")
        print(f"Showing first {num_rows} rows:\n")

        # Fetch and display sample data
        df = conn.execute(f"SELECT * FROM {table_name} LIMIT {num_rows}").fetchdf()

        # For wide tables, show in transposed format
        if len(df.columns) > 15:
            print("(Showing in transposed format due to many columns)\n")
            for idx in range(len(df)):
                print(f"\n--- Row {idx + 1} ---")
                for col in df.columns:
                    value = df.iloc[idx][col]
                    # Truncate long values
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    print(f"  {col}: {value_str}")
        else:
            print(df.to_string(index=False))

        print("\n")

    conn.close()


if __name__ == "__main__":
    view_samples()
