"""Extract enum values for target_audience and manager_type from the database."""

import duckdb

DB_PATH = "src/infrastructure/database/br_funds.db"

conn = duckdb.connect(DB_PATH, read_only=True)

# Get all distinct target_audience values
print("=" * 80)
print("TARGET AUDIENCE VALUES")
print("=" * 80)
target_audience = conn.execute("""
    SELECT DISTINCT target_audience, COUNT(*) as count
    FROM funds
    WHERE target_audience IS NOT NULL AND target_audience != 'UNSPECIFIED'
    GROUP BY target_audience
    ORDER BY count DESC
""").fetchall()

print(f"\nTotal distinct values: {len(target_audience)}\n")
print(f"{'Value':<30} {'Count':>10}")
print("-" * 42)
for value, count in target_audience:
    print(f"{value:<30} {count:>10,}")

# Get all distinct manager_type values
print("\n" + "=" * 80)
print("MANAGER TYPE VALUES")
print("=" * 80)
manager_type = conn.execute("""
    SELECT DISTINCT manager_type, COUNT(*) as count
    FROM funds
    WHERE manager_type IS NOT NULL AND manager_type != 'UNSPECIFIED'
    GROUP BY manager_type
    ORDER BY count DESC
""").fetchall()

print(f"\nTotal distinct values: {len(manager_type)}\n")
print(f"{'Value':<30} {'Count':>10}")
print("-" * 42)
for value, count in manager_type:
    print(f"{value:<30} {count:>10,}")

# Check boolean fields statistics
print("\n" + "=" * 80)
print("BOOLEAN FIELDS STATISTICS")
print("=" * 80)

fields = [
    "is_fund_of_funds",
    "is_exclusive_fund",
    "can_invest_abroad_100_pct",
    "has_long_term_taxation"
]

for field in fields:
    print(f"\n{field}:")
    results = conn.execute(f"""
        SELECT {field}, COUNT(*) as count
        FROM funds
        WHERE {field} IS NOT NULL
        GROUP BY {field}
        ORDER BY count DESC
    """).fetchall()

    for value, count in results:
        print(f"  {value}: {count:,}")

conn.close()

print("\n" + "=" * 80)
