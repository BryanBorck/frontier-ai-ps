# Benchmarks Ingestion

This directory handles the ingestion of market benchmarks (CDI, SELIC, IBOVESPA, IFIX) for performance comparisons.

## Data Sources
- **CDI & SELIC:** Banco Central do Brasil (BCB) API.
  - *Current Status:* Automated ingestion via `requests` faces 406 Not Acceptable errors (blocking bots). Ingestion script attempts to fetch but might default to empty or require manual run/headers tuning.
- **IBOVESPA & IFIX:** Yahoo Finance (`yfinance`).
  - *Current Status:* Working successfully for IBOVESPA (`^BVSP`).

## Scripts
- `ingest_benchmarks.py`: Fetches data from BCB (codes 11/12) and Yahoo Finance, consolidates into DuckDB.

## Database
- **Path:** `src/infrastructure/database/benchmarks.db`
- **Table:** `benchmarks` (date DATE, symbol VARCHAR, value DOUBLE)

## Usage
```bash
uv run --with yfinance --with pandas --with requests --with duckdb src/infrastructure/ingestion/benchmarks/ingest_benchmarks.py
```

## Known Issues
- BCB API returns 406 for cloud IP ranges/requests without specific headers. Current workaround relies on Yahoo Finance for IBOV. CDI data needs alternative sourcing or manual upload if critical.

