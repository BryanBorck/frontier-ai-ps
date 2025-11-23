import duckdb
import pandas as pd

BR_FUNDS_PATH = "src/infrastructure/database/br_funds.db"
LAMINA_PATH = "src/infrastructure/database/cvm_lamina.db"

def check_join_possibility():
    # Connect to br_funds.db
    conn = duckdb.connect(BR_FUNDS_PATH)
    
    # Get a sample fund from br_funds
    print(f"--- Sample from br_funds.db (funds table) ---")
    query_funds = """
        SELECT 
            fund_id, 
            identifiers, 
            legal_name 
        FROM funds 
        LIMIT 3
    """
    funds_sample = conn.execute(query_funds).fetchdf()
    print(funds_sample.to_string())
    
    # Extract how CNPJ looks in identifiers
    # identifiers is likely a list of structs
    print("\n--- Inspecting Identifiers Structure ---")
    # We'll pick the first row's identifiers
    first_id = funds_sample.iloc[0]['identifiers']
    print(f"Identifiers (Raw): {first_id}")
    
    conn.close()
    
    # Connect to cvm_lamina.db
    conn = duckdb.connect(LAMINA_PATH)
    print(f"\n--- Sample from cvm_lamina.db (laminas_clean) ---")
    query_lamina = """
        SELECT 
            fund_id,
            cnpj_formatted, 
            legal_name 
        FROM laminas_clean 
        LIMIT 3
    """
    lamina_sample = conn.execute(query_lamina).fetchdf()
    print(lamina_sample.to_string())
    
    conn.close()

if __name__ == "__main__":
    check_join_possibility()

