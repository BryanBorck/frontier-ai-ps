import duckdb

CVM_DB_PATH = "src/infrastructure/database/cvm_lamina.db"
BR_FUNDS_DB_PATH = "src/infrastructure/database/br_funds.db"


def match_funds():
    print("Linking Laminas to Master Funds Table...")
    conn = duckdb.connect(CVM_DB_PATH)

    # Attach the master DB
    conn.execute(f"ATTACH '{BR_FUNDS_DB_PATH}' AS master_db")

    # 1. Create a temporary mapping table from Master DB
    # Extract CNPJ and UUID from master_db.funds
    # We filter identifiers list to find the one with type='CNPJ'
    conn.execute("""
        CREATE TEMP TABLE master_cnpjs AS
        SELECT 
            fund_id AS master_uuid,
            list_filter(identifiers, x -> x.type = 'CNPJ')[1].value AS cnpj
        FROM master_db.funds
        WHERE list_filter(identifiers, x -> x.type = 'CNPJ') IS NOT NULL
    """)

    # 2. Update laminas_clean with the Master UUID
    # First, rename the current placeholder fund_id to something else to avoid confusion
    conn.execute("ALTER TABLE laminas_clean RENAME COLUMN fund_id TO fund_id_cnpj_struct")

    # Add column for the real Master ID
    conn.execute("ALTER TABLE laminas_clean ADD COLUMN fund_id STRUCT(type VARCHAR, value VARCHAR)")

    # 3. Perform the Update via Update Join logic (using a merge or update from subquery)
    # DuckDB UPDATE FROM syntax
    print("Updating IDs...")
    conn.execute("""
        UPDATE laminas_clean
        SET fund_id = master_cnpjs.master_uuid
        FROM master_cnpjs
        WHERE laminas_clean.cnpj_formatted = master_cnpjs.cnpj
    """)

    # 4. Stats
    total_rows = conn.execute("SELECT COUNT(*) FROM laminas_clean").fetchone()[0]
    matched_rows = conn.execute(
        "SELECT COUNT(*) FROM laminas_clean WHERE fund_id IS NOT NULL"
    ).fetchone()[0]

    print(f"Total Laminas: {total_rows}")
    print(f"Matched with Master DB: {matched_rows}")
    print(
        f"Unmatched: {total_rows - matched_rows} (These funds might be new or missing from master list)"
    )

    # 5. Cleanup: Keep the new fund_id as the primary one.
    # If unmatched, fund_id is NULL. We might want to fallback to the generated hash or keep it NULL to indicate "not in master".
    # For now, let's look at a sample of matched rows.

    print("\n--- Sample Matched Rows ---")
    sample = conn.execute("""
        SELECT fund_id, cnpj_formatted, legal_name 
        FROM laminas_clean 
        WHERE fund_id IS NOT NULL 
        LIMIT 5
    """).fetchdf()
    print(sample.to_string())

    # Detach
    conn.execute("DETACH master_db")
    conn.close()


if __name__ == "__main__":
    match_funds()
