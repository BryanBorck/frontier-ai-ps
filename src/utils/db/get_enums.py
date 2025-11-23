"""Get distinct values for fund_type and investment_class to create enums."""

import duckdb


def get_fund_enums(db_path: str = "docs/br_funds.db"):
    """Get distinct values for fund_type and investment_class."""
    conn = duckdb.connect(db_path, read_only=True)

    # Get fund_type values
    print("=" * 80)
    print("FUND_TYPE values:")
    print("=" * 80)
    fund_types = conn.execute(
        """
        SELECT fund_type, COUNT(*) as count
        FROM funds
        WHERE fund_type IS NOT NULL AND fund_type != ''
        GROUP BY fund_type
        ORDER BY count DESC
        """
    ).fetchall()

    for fund_type, count in fund_types:
        print(f"  {fund_type:30s} - {count:,} funds")

    # Get investment_class values
    print("\n" + "=" * 80)
    print("INVESTMENT_CLASS values:")
    print("=" * 80)
    investment_classes = conn.execute(
        """
        SELECT investment_class, COUNT(*) as count
        FROM funds
        WHERE investment_class IS NOT NULL AND investment_class != ''
        GROUP BY investment_class
        ORDER BY count DESC
        """
    ).fetchall()

    for inv_class, count in investment_classes:
        print(f"  {inv_class:30s} - {count:,} funds")

    conn.close()


if __name__ == "__main__":
    get_fund_enums()
