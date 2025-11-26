import duckdb
import pandas as pd

# Configuration
DB_PATH = "src/infrastructure/database/cvm_lamina.db"

def inspect_data():
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

    # Inspect 'laminas' table
    print("\n--- Schema for 'laminas' ---")
    schema = conn.execute("DESCRIBE laminas").fetchdf()
    print(schema)
    
    print("\n--- Sample Data (checking for special chars) ---")
    # Select columns likely to have Portuguese text
    text_cols = ["DENOM_SOCIAL", "OBJETIVO", "POLIT_INVEST", "PUBLICO_ALVO"]
    
    # Check if these columns exist
    available_cols = [col for col in text_cols if col in schema['column_name'].values]
    
    if available_cols:
        query = f"SELECT {', '.join(available_cols)} FROM laminas LIMIT 5"
        df = conn.execute(query).fetchdf()
        
        # Print full text for inspection
        pd.set_option('display.max_colwidth', None)
        print(df.to_string())
    else:
        print("Target text columns not found in schema.")

    conn.close()

import os
if __name__ == "__main__":
    inspect_data()

