"""Extract all distinct fund types and investment classes from the database."""

import duckdb

DB_PATH = "src/infrastructure/db/br_funds.db"

conn = duckdb.connect(DB_PATH, read_only=True)

# Get all distinct fund types
print("=" * 80)
print("FUND TYPES")
print("=" * 80)
fund_types = conn.execute("""
    SELECT DISTINCT fund_type
    FROM funds
    WHERE fund_type IS NOT NULL
    ORDER BY fund_type
""").fetchall()

print(f"\nTotal distinct fund types: {len(fund_types)}\n")
for ft in fund_types:
    print(f"  - {ft[0]}")

# Get all distinct investment classes
print("\n" + "=" * 80)
print("INVESTMENT CLASSES")
print("=" * 80)
investment_classes = conn.execute("""
    SELECT DISTINCT investment_class
    FROM funds
    WHERE investment_class IS NOT NULL
    ORDER BY investment_class
""").fetchall()

print(f"\nTotal distinct investment classes: {len(investment_classes)}\n")
for ic in investment_classes:
    print(f"  - {ic[0]}")

# Get count of records for each fund type
print("\n" + "=" * 80)
print("FUND TYPE COUNTS")
print("=" * 80)
fund_type_counts = conn.execute("""
    SELECT fund_type, COUNT(*) as count
    FROM funds
    WHERE fund_type IS NOT NULL
    GROUP BY fund_type
    ORDER BY count DESC
""").fetchall()

print(f"\n{'Fund Type':<30} {'Count':>10}")
print("-" * 42)
for ft, count in fund_type_counts:
    print(f"{ft:<30} {count:>10,}")

# Get count of records for each investment class
print("\n" + "=" * 80)
print("INVESTMENT CLASS COUNTS")
print("=" * 80)
investment_class_counts = conn.execute("""
    SELECT investment_class, COUNT(*) as count
    FROM funds
    WHERE investment_class IS NOT NULL
    GROUP BY investment_class
    ORDER BY count DESC
""").fetchall()

print(f"\n{'Investment Class':<30} {'Count':>10}")
print("-" * 42)
for ic, count in investment_class_counts:
    print(f"{ic:<30} {count:>10,}")

conn.close()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total distinct fund types: {len(fund_types)}")
print(f"Total distinct investment classes: {len(investment_classes)}")
