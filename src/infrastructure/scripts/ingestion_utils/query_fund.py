import duckdb
import pandas as pd

DB_PATH = "src/infrastructure/database/cvm_lamina.db"

def get_fund_details(cnpj):
    conn = duckdb.connect(DB_PATH)
    
    print(f"--- Details for CNPJ: {cnpj} ---")
    
    # Normalize CNPJ input if needed (strip punct)
    # But in DB we kept cnpj_formatted as "XX.XXX.XXX/XXXX-XX"
    
    query = f"""
        SELECT * 
        FROM laminas_clean 
        WHERE cnpj_formatted = '{cnpj}'
    """
    
    df = conn.execute(query).fetchdf()
    
    if df.empty:
        print("Fund not found.")
    else:
        # Transpose for better readability of single record
        pd.set_option('display.max_colwidth', None)
        print(df.T.to_string())
        
    conn.close()

if __name__ == "__main__":
    get_fund_details("37.235.773/0001-67")

