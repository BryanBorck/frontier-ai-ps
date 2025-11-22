import duckdb


def check_db():
    try:
        conn = duckdb.connect("src/infrastructure/db/br_funds.db", read_only=True)
        total = conn.execute("SELECT COUNT(*) FROM funds").fetchone()[0]
        missing = conn.execute(
            "SELECT COUNT(*) FROM funds WHERE service_providers IS NULL OR len(service_providers) = 0"
        ).fetchone()[0]
        print(f"Total: {total}")
        print(f"Missing: {missing}")
        print(f"Missing %: {missing / total * 100:.2f}%")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_db()
