"""Extract and display sample records from the Brazilian funds database.

This utility helps understand the database structure by showing actual data samples.
"""

import json

import duckdb

DB_PATH = "src/infrastructure/db/br_funds.db"


def print_separator(char="=", length=120):
    """Print a separator line."""
    print(char * length)


def format_value(value, max_width=50):
    """Format a value for display, truncating if necessary."""
    if value is None:
        return "NULL"

    str_value = str(value)

    # If it's a list or dict, format as JSON
    if isinstance(value, (list, dict)):
        try:
            str_value = json.dumps(value, ensure_ascii=False)
        except:
            str_value = str(value)

    # Truncate if too long
    if len(str_value) > max_width:
        return str_value[:max_width-3] + "..."

    return str_value


def extract_sample_records(limit=25):
    """Extract and display sample records from the database.

    Args:
        limit: Number of records to extract (default: 25)
    """
    conn = duckdb.connect(DB_PATH, read_only=True)

    # Get table schema
    print_separator()
    print("DATABASE SCHEMA")
    print_separator()

    schema = conn.execute("PRAGMA table_info(funds)").fetchall()
    print(f"\n{'Column':<30} {'Type':<20} {'Nullable':<10}")
    print("-" * 60)
    for col in schema:
        col_name = col[1]
        col_type = col[2]
        nullable = "YES" if col[3] == 0 else "NO"
        print(f"{col_name:<30} {col_type:<20} {nullable:<10}")

    # Get total count
    total_count = conn.execute("SELECT COUNT(*) FROM funds").fetchone()[0]
    print(f"\nTotal records in database: {total_count:,}")

    # Extract sample records
    print(f"\n")
    print_separator()
    print(f"SAMPLE RECORDS (First {limit} records)")
    print_separator()

    # Get all columns
    query = f"""
        SELECT *
        FROM funds
        LIMIT {limit}
    """

    result = conn.execute(query)
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()

    # Display each record
    for idx, row in enumerate(rows, 1):
        print(f"\n{'─' * 120}")
        print(f"RECORD #{idx}")
        print(f"{'─' * 120}")

        for col_name, value in zip(columns, row):
            formatted_value = format_value(value, max_width=80)
            print(f"{col_name:<30} : {formatted_value}")

    # Summary statistics
    print(f"\n")
    print_separator()
    print("SUMMARY STATISTICS")
    print_separator()

    # Count by fund type
    print("\nFund Types (Top 10):")
    fund_types = conn.execute("""
        SELECT fund_type, COUNT(*) as count
        FROM funds
        WHERE fund_type IS NOT NULL
        GROUP BY fund_type
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()

    print(f"{'Type':<20} {'Count':>10}")
    print("-" * 32)
    for ft, count in fund_types:
        print(f"{ft:<20} {count:>10,}")

    # Count by investment class
    print("\nInvestment Classes (Top 10):")
    inv_classes = conn.execute("""
        SELECT investment_class, COUNT(*) as count
        FROM funds
        WHERE investment_class IS NOT NULL AND investment_class != ''
        GROUP BY investment_class
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()

    print(f"{'Class':<25} {'Count':>10}")
    print("-" * 37)
    for ic, count in inv_classes:
        print(f"{ic:<25} {count:>10,}")

    conn.close()

    print(f"\n")
    print_separator()
    print(f"Extraction complete! Displayed {len(rows)} records.")
    print_separator()


if __name__ == "__main__":
    import sys

    # Allow custom limit from command line
    limit = 25
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid limit: {sys.argv[1]}, using default: 25")

    extract_sample_records(limit=limit)
