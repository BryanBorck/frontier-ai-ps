# CVM Lamina Ingestion

This directory handles the ingestion of CVM "Lâmina" (Fact Sheet) data.

## Data Source

- **URL:** `https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/`
- **Frequency:** Monthly
- **Content:** Key information documents for investment funds (Objectives, Policy, Target Audience, Fees, etc.).

## Scripts

- `ingest_lamina.py`: Downloads the last 3 months of data (handling lag), ingests all available CSVs in `data/` folder into DuckDB, and deduplicates to keep the latest record per fund.

## Database

- **Path:** `src/infrastructure/database/cvm_lamina.db`
- **Table:** `laminas` (Latest snapshot of fund lamina data)

## Usage

Run the ingestion script:

```bash
uv run src/infrastructure/ingestion/cvm/lamina/ingest_lamina.py
```
