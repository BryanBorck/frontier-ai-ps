from src.infrastructure.ingestion.vectors.processor import VectorIngestor

# Configuration
BR_FUNDS_DB = "src/infrastructure/database/br_funds.db"
CVM_LAMINA_DB = "src/infrastructure/database/cvm_lamina.db"
VECTOR_DB_PATH = "src/infrastructure/database/vector_store.db"

def main():
    ingestor = VectorIngestor(
        funds_db_path=BR_FUNDS_DB,
        lamina_db_path=CVM_LAMINA_DB,
        vector_db_path=VECTOR_DB_PATH
    )
    ingestor.build()

if __name__ == "__main__":
    main()

