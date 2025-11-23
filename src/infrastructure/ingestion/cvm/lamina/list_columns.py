import duckdb

DB_PATH = "src/infrastructure/database/cvm_lamina.db"

def list_columns():
    conn = duckdb.connect(DB_PATH)
    
    # Get detailed column info
    df = conn.execute("DESCRIBE laminas").fetchdf()
    
    print(f"Total Rows: {conn.execute('SELECT COUNT(*) FROM laminas').fetchone()[0]}")
    print(f"Total Columns: {len(df)}")
    print("\nColumns:")
    for col in df['column_name'].tolist():
        print(f"- {col}")
        
    conn.close()

if __name__ == "__main__":
    list_columns()

