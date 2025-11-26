from src.infrastructure.ingestion.metrics.processor import MetricsCalculator

# Paths
FUNDS_DB = "src/infrastructure/database/br_funds.db"
BENCHMARKS_DB = "src/infrastructure/database/benchmarks.db"

def main():
    calculator = MetricsCalculator(funds_db_path=FUNDS_DB, benchmarks_db_path=BENCHMARKS_DB)
    calculator.calculate()

if __name__ == "__main__":
    main()

