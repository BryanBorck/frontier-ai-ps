import duckdb
import os

DB_PATH = "src/infrastructure/database/benchmarks.db"

def inspect_benchmarks():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = duckdb.connect(DB_PATH)
    
    print(f"--- Inspecting {DB_PATH} ---")
    
    # Get table info
    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"Tables: {tables}")
    
    if not tables:
        print("No tables found.")
        return

    # Inspect 'benchmarks' table
    print("\n--- Schema for 'benchmarks' ---")
    schema = conn.execute("DESCRIBE benchmarks").fetchdf()
    print(schema)
    
    print("\n--- Sample Data ---")
    query = "SELECT * FROM benchmarks ORDER BY date DESC LIMIT 5"
    df = conn.execute(query).fetchdf()
    print(df.to_string())
    
    print("\n--- Symbols ---")
    symbols = conn.execute("SELECT DISTINCT symbol FROM benchmarks").fetchdf()
    print(symbols.to_string())

    conn.close()

if __name__ == "__main__":
    inspect_benchmarks()

