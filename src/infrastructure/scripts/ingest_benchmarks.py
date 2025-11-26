from src.infrastructure.ingestion.benchmarks.processor import BenchmarkIngestor

# Configuration
DB_PATH = "src/infrastructure/database/benchmarks.db"

def main():
    ingestor = BenchmarkIngestor(db_path=DB_PATH)
    ingestor.ingest()

if __name__ == "__main__":
    main()

