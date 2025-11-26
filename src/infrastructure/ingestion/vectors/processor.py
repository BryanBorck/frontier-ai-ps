import duckdb
import pandas as pd
import tqdm
from sentence_transformers import SentenceTransformer


class VectorIngestor:
    """
    Builds and stores vector embeddings for funds.
    """

    # Model: Multilingual MiniLM L12 v2 (Good for Portuguese, fast, 384 dims)
    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    BATCH_SIZE = 500

    def __init__(self, funds_db_path: str, lamina_db_path: str, vector_db_path: str):
        self.funds_db = funds_db_path
        self.lamina_db = lamina_db_path
        self.vector_db = vector_db_path

    def load_data(self) -> pd.DataFrame:
        """
        Joins Master Data (br_funds) with Qualitative Data (cvm_lamina).
        """
        print("Loading and joining data from databases...")
        conn = duckdb.connect(self.funds_db)
        conn.execute(f"ATTACH '{self.lamina_db}' AS cvm_db")

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
                -- Fields from Lamina
                l.objective,
                l.investment_policy,
                l.benchmark,
                l.risk_class_admin,
                l.min_initial_investment,
                -- Extra Metadata
                list_filter(f.identifiers, x -> x.type = 'CNPJ')[1].value as cnpj
            FROM funds f
            LEFT JOIN cvm_db.laminas_clean l ON f.fund_id = l.fund_id
            WHERE f.status != 'CANCELLED'
        """

        df = conn.execute(query).fetchdf()
        conn.close()

        print(f"Loaded {len(df)} active funds with qualitative data.")
        return df

    def generate_text_representation(self, row):
        """
        Constructs the rich text block for embedding.
        """
        # Risk
        risk_score = row["risk_class_admin"]
        risk_text = "Unknown"
        try:
            if risk_score:
                r = int(risk_score)
                if r <= 2:
                    risk_text = "Low / Conservative"
                elif r <= 5:
                    risk_text = "Moderate / Balanced"
                else:
                    risk_text = "High / Aggressive / Volatile"
        except Exception:
            pass

        # Access
        min_inv = row["min_initial_investment"]
        access_text = "Unknown"
        if pd.notnull(min_inv):
            if min_inv <= 500:
                access_text = "Accessible (Low Minimum)"
            elif min_inv <= 5000:
                access_text = "Standard Retail"
            elif min_inv >= 100000:
                access_text = "High Net Worth / Private"

        # Global
        global_text = "Domestic Brazil"
        if row["can_invest_abroad_100_pct"]:
            global_text = "International Exposure / Offshore"

        # Service Providers
        manager = "Unknown Manager"
        administrator = "Unknown Administrator"

        providers = row["service_providers"]
        try:
            if providers is not None and len(providers) > 0:
                for p in providers:
                    if isinstance(p, dict):
                        if p.get("type") == "MANAGER":
                            manager = p.get("name", manager)
                        elif p.get("type") == "ADMINISTRATOR":
                            administrator = p.get("name", administrator)
        except Exception:
            pass

        # Text Construction
        text_parts = [
            f"Fund Name: {row['legal_name']}",
            f"Category: {row['investment_class']} | Type: {row['fund_type']}",
            f"Manager: {manager} | Administrator: {administrator}",
            f"Benchmark: {row['benchmark'] if pd.notnull(row['benchmark']) else 'N/A'}",
            f"Risk Profile: {risk_text}",
            f"Access: {access_text} | Audience: {row['target_audience']}",
            f"Focus: {global_text}",
            f"Strategy Description: {row['objective'] if pd.notnull(row['objective']) else ''}",
            f"Investment Policy: {row['investment_policy'] if pd.notnull(row['investment_policy']) else ''}",
        ]

        return "\n".join(text_parts)

    def build(self):
        # 1. Data Prep
        df = self.load_data()
        if df.empty:
            print("No funds found to vectorize.")
            return

        print("Constructing text documents...")
        df["text_content"] = df.apply(self.generate_text_representation, axis=1)

        # 2. Embedding Generation
        print(f"Loading Model: {self.MODEL_NAME}...")
        model = SentenceTransformer(self.MODEL_NAME)

        embeddings = []
        texts = df["text_content"].tolist()

        print(f"Generating embeddings for {len(texts)} documents...")
        for i in tqdm.tqdm(range(0, len(texts), self.BATCH_SIZE)):
            batch_texts = texts[i : i + self.BATCH_SIZE]
            batch_embeddings = model.encode(batch_texts, convert_to_numpy=True)
            embeddings.extend(batch_embeddings)

        df["embedding"] = list(embeddings)

        # 3. Storage
        print(f"Saving to {self.vector_db}...")
        conn = duckdb.connect(self.vector_db)

        conn.execute("DROP TABLE IF EXISTS fund_embeddings")

        conn.execute("""
            CREATE TABLE fund_embeddings (
                fund_uuid VARCHAR,
                cnpj VARCHAR,
                text_content VARCHAR,
                embedding FLOAT[384],
                metadata STRUCT(legal_name VARCHAR, investment_class VARCHAR)
            )
        """)

        # Prepare DF for insertion
        insert_df = pd.DataFrame(
            {
                "fund_uuid": df["fund_id"],
                "cnpj": df["cnpj"],
                "text_content": df["text_content"],
                "embedding": df["embedding"],
                "metadata": df.apply(
                    lambda r: {
                        "legal_name": r["legal_name"],
                        "investment_class": r["investment_class"],
                    },
                    axis=1,
                ),
            }
        )

        conn.execute("INSERT INTO fund_embeddings SELECT * FROM insert_df")

        # Verify
        count = conn.execute("SELECT COUNT(*) FROM fund_embeddings").fetchone()[0]
        print(f"Successfully stored {count} vector embeddings.")

        # Sanity Check
        print("\n--- Sanity Check: Closest match to 'Ouro' (Gold) ---")
        test_vec = model.encode("fundo de investimento em ouro", convert_to_numpy=True)

        query = """
            SELECT metadata['legal_name'], text_content, array_cosine_similarity(embedding, ?::FLOAT[384]) as score
            FROM fund_embeddings
            ORDER BY score DESC
            LIMIT 1
        """
        result = conn.execute(query, [test_vec]).fetchall()
        for row in result:
            print(f"Match: {row[0]} (Score: {row[2]:.4f})")

        conn.close()

