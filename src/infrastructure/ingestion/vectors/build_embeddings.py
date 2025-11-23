import duckdb
import pandas as pd
from sentence_transformers import SentenceTransformer
import os
import tqdm

# Configuration
BR_FUNDS_DB = "src/infrastructure/database/br_funds.db"
CVM_LAMINA_DB = "src/infrastructure/database/cvm_lamina.db"
VECTOR_DB_PATH = "src/infrastructure/database/vector_store.db"

# Model: Multilingual MiniLM L12 v2 (Good for Portuguese, fast, 384 dims)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
BATCH_SIZE = 500  # Conservative batch size for 36GB RAM system

def load_data():
    """
    Joins Master Data (br_funds) with Qualitative Data (cvm_lamina).
    """
    print("Loading and joining data from databases...")
    conn = duckdb.connect(BR_FUNDS_DB)
    conn.execute(f"ATTACH '{CVM_LAMINA_DB}' AS cvm_db")
    
    # We join on the matched fund_id (UUID)
    # We prioritize funds that have qualitative data (inner join or left join?)
    # Let's do INNER JOIN for now to only vectorise funds we have rich text for.
    # OR Left Join and fill missing text with placeholders if we want to search ALL funds?
    # Given the Semantic Search is mostly for the qualitative part, Inner Join on Lamina makes sense.
    # BUT, br_funds has ~60k funds, laminas might have fewer matched.
    
    query = """
        SELECT 
            f.fund_id,
            f.legal_name,
            f.investment_class,
            f.fund_type,
            f.target_audience,
            f.status,
            f.can_invest_abroad_100_pct,
            f.is_exclusive_fund,
            f.service_providers,
            -- Fields from Lamina (might be NULL in Left Join)
            l.objective,
            l.investment_policy,
            l.benchmark,
            l.risk_class_admin,
            l.min_initial_investment,
            -- Extra Metadata for context
            list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value as cnpj
        FROM funds f
        LEFT JOIN cvm_db.laminas_clean l ON f.fund_id = l.fund_id
        WHERE f.status != 'CANCELLED' -- Index everything except explicitly cancelled
    """
    
    df = conn.execute(query).fetchdf()
    conn.close()
    
    print(f"Loaded {len(df)} active funds with qualitative data.")
    return df

def generate_text_representation(row):
    """
    Constructs the rich text block for embedding.
    """
    # 1. Mappings
    # Risk
    risk_score = row['risk_class_admin']
    risk_text = "Unknown"
    try:
        if risk_score:
            r = int(risk_score)
            if r <= 2: risk_text = "Low / Conservative"
            elif r <= 5: risk_text = "Moderate / Balanced"
            else: risk_text = "High / Aggressive / Volatile"
    except: pass
    
    # Access
    min_inv = row['min_initial_investment']
    access_text = "Unknown"
    if pd.notnull(min_inv):
        if min_inv <= 500: access_text = "Accessible (Low Minimum)"
        elif min_inv <= 5000: access_text = "Standard Retail"
        elif min_inv >= 100000: access_text = "High Net Worth / Private"
    
    # Global
    global_text = "Domestic Brazil"
    if row['can_invest_abroad_100_pct']:
        global_text = "International Exposure / Offshore"

    # Service Providers
    manager = "Unknown Manager"
    administrator = "Unknown Administrator"
    
    providers = row['service_providers']
    # Handle potential numpy array or list
    try:
        if providers is not None and len(providers) > 0:
             for p in providers:
                # DuckDB STRUCTs often come as dicts in pandas
                if isinstance(p, dict):
                    if p.get('type') == 'MANAGER':
                        manager = p.get('name', manager)
                    elif p.get('type') == 'ADMINISTRATOR':
                        administrator = p.get('name', administrator)
    except Exception:
        pass
    
    # 2. Text Construction
    # We use explicit prefixes to help the model distinguish sections
    text_parts = [
        f"Fund Name: {row['legal_name']}",
        f"Category: {row['investment_class']} | Type: {row['fund_type']}",
        f"Manager: {manager} | Administrator: {administrator}",
        f"Benchmark: {row['benchmark'] if pd.notnull(row['benchmark']) else 'N/A'}",
        f"Risk Profile: {risk_text}",
        f"Access: {access_text} | Audience: {row['target_audience']}",
        f"Focus: {global_text}",
        f"Strategy Description: {row['objective'] if pd.notnull(row['objective']) else ''}",
        f"Investment Policy: {row['investment_policy'] if pd.notnull(row['investment_policy']) else ''}"
    ]
    
    return "\n".join(text_parts)

def build_vector_store():
    # 1. Data Prep
    df = load_data()
    if df.empty:
        print("No funds found to vectorize.")
        return

    print("Constructing text documents...")
    df['text_content'] = df.apply(generate_text_representation, axis=1)
    
    # 2. Embedding Generation
    print(f"Loading Model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    # Calculate embeddings in batches
    embeddings = []
    texts = df['text_content'].tolist()
    
    print(f"Generating embeddings for {len(texts)} documents...")
    for i in tqdm.tqdm(range(0, len(texts), BATCH_SIZE)):
        batch_texts = texts[i : i + BATCH_SIZE]
        batch_embeddings = model.encode(batch_texts, convert_to_numpy=True)
        embeddings.extend(batch_embeddings)
    
    df['embedding'] = list(embeddings)
    
    # 3. Storage
    print(f"Saving to {VECTOR_DB_PATH}...")
    conn = duckdb.connect(VECTOR_DB_PATH)
    
    conn.execute("DROP TABLE IF EXISTS fund_embeddings")
    
    # Create table with ARRAY type (Float32[384])
    # DuckDB handles numpy arrays automatically in Python API usually, but explicit typing is safer.
    # 384 is the dim of MiniLM-L12-v2
    conn.execute("""
        CREATE TABLE fund_embeddings (
            fund_uuid VARCHAR,
            cnpj VARCHAR,
            text_content VARCHAR,
            embedding FLOAT[384],
            metadata STRUCT(legal_name VARCHAR, investment_class VARCHAR)
        )
    """)
    
    # Insert data
    # We prepare a clean DF for insertion
    insert_df = pd.DataFrame({
        'fund_uuid': df['fund_id'],
        'cnpj': df['cnpj'],
        'text_content': df['text_content'],
        'embedding': df['embedding'],
        'metadata': df.apply(lambda r: {'legal_name': r['legal_name'], 'investment_class': r['investment_class']}, axis=1)
    })
    
    conn.execute("INSERT INTO fund_embeddings SELECT * FROM insert_df")
    
    # Verify
    count = conn.execute("SELECT COUNT(*) FROM fund_embeddings").fetchone()[0]
    print(f"Successfully stored {count} vector embeddings.")
    
    # Test Similarity Search (Sanity Check)
    print("\n--- Sanity Check: Closest match to 'Ouro' (Gold) ---")
    test_vec = model.encode("fundo de investimento em ouro", convert_to_numpy=True)
    
    # DuckDB Vector Search: array_cosine_similarity
    # We order by descending similarity
    query = f"""
        SELECT metadata['legal_name'], text_content, array_cosine_similarity(embedding, ?::FLOAT[384]) as score
        FROM fund_embeddings
        ORDER BY score DESC
        LIMIT 1
    """
    result = conn.execute(query, [test_vec]).fetchall()
    for row in result:
        print(f"Match: {row[0]} (Score: {row[2]:.4f})")
    
    conn.close()

if __name__ == "__main__":
    build_vector_store()

