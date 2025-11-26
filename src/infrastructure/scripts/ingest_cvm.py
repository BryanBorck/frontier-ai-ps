from src.infrastructure.ingestion.cvm.processor import CVMDataIngestor

# Configuration
DOWNLOAD_DIR = "src/infrastructure/ingestion/cvm/lamina/data"
DB_PATH = "src/infrastructure/database/cvm_lamina.db"

def main():
    ingestor = CVMDataIngestor(download_dir=DOWNLOAD_DIR, db_path=DB_PATH)
    ingestor.ingest()

if __name__ == "__main__":
    main()

