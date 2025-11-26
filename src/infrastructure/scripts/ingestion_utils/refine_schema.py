import duckdb

DB_PATH = "src/infrastructure/database/cvm_lamina.db"

def refine_schema():
    conn = duckdb.connect(DB_PATH)
    
    print("Refining schema...")
    
    # Drop if exists
    conn.execute("DROP TABLE IF EXISTS laminas_clean")
    
    # Create cleaned table with selected columns and normalized identifiers
    # We want:
    # 1. Identifiers (CNPJ normalized)
    # 2. Fund Name
    # 3. Qualitative info (Objective, Policy, Target Audience)
    # 4. Liquidity & Fees (Redemption, Mgmt Fee, Performance Fee)
    # 5. Benchmarks
    # 6. Risk
    
    # Normalization logic for CNPJ: 
    # Currently it is string "XX.XXX.XXX/XXXX-XX". We can keep it as string but maybe strip punctuation if needed.
    # The br_funds.db uses STRUCT(type, value). We can construct that.
    
    query = """
        CREATE TABLE laminas_clean AS
        SELECT 
            -- Identifiers
            {'type': 'CNPJ', 'value': regexp_replace(CNPJ_FUNDO_CLASSE, '[^0-9]', '', 'g')} AS fund_id,
            CNPJ_FUNDO_CLASSE AS cnpj_formatted,
            DENOM_SOCIAL AS legal_name,
            NM_FANTASIA AS fantasy_name,
            
            -- Dates
            DT_COMPTC AS last_update,
            
            -- Qualitative
            PUBLICO_ALVO AS target_audience,
            OBJETIVO AS objective,
            POLIT_INVEST AS investment_policy,
            
            -- Risk & Restrictions
            CLASSE_RISCO_ADMIN AS risk_class_admin,
            RISCO_PERDA AS loss_risk_warning,
            RESTR_INVEST AS investment_restrictions,
            
            -- Asset Allocation Limits (%)
            PR_PL_ATIVO_EXTERIOR AS max_foreign_investment_pct,
            PR_PL_ATIVO_CRED_PRIV AS max_credit_priv_investment_pct,
            PR_PL_ALAVANC AS max_leverage_pct,
            
            -- Fees & Expenses
            TAXA_ADM AS management_fee,
            TAXA_PERFM AS performance_fee,
            TAXA_SAIDA AS exit_fee,
            
            -- Liquidity
            RESGATE_MIN AS min_redemption_amount,
            INVEST_INICIAL_MIN AS min_initial_investment,
            QT_DIA_CONVERSAO_COTA_RESGATE AS redemption_quote_days,
            QT_DIA_PAGTO_RESGATE AS redemption_payment_days,
            
            -- Performance
            INDICE_REFER AS benchmark,
            RENTAB_GATILHO AS benchmark_trigger,
            
            -- Contact
            ENDER_ELETRONICO AS website
            
        FROM laminas
    """
    
    conn.execute(query)
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM laminas_clean").fetchone()[0]
    print(f"Created 'laminas_clean' with {count} rows.")
    
    cols = conn.execute("DESCRIBE laminas_clean").fetchdf()
    print("\nNew Schema:")
    print(cols[['column_name', 'column_type']])
    
    conn.close()

if __name__ == "__main__":
    refine_schema()

