# Frontier AI Fund Search - Infrastructure Documentation

## Overview
This infrastructure layer handles the ingestion, storage, and processing of all financial data.

## Directory Structure

### `database/`
Contains the DuckDB database files.
- `br_funds.db`: Main database with funds, daily snapshots, and calculated metrics.
- `benchmarks.db`: Market benchmarks (IBOVESPA, CDI).
- `cvm_lamina.db`: Qualitative data from CVM Fact Sheets (Lâminas).

### `ingestion/`
Scripts for fetching and processing raw data.
- `cvm/lamina/`: Ingests "Lâmina" data (Objectives, Policies).
- `benchmarks/`: Ingests market indices (BCB, Yahoo Finance).
- `metrics/`: Calculates derived metrics (Sharpe, Volatility, Beta).

## Data Flow
1.  **Raw Ingestion:** Scripts in `ingestion/` fetch data from APIs/CVM.
2.  **Storage:** Data is stored in `database/` files.
3.  **Processing:** `metrics/calculate_metrics.py` reads from DBs, computes stats, and writes back to `br_funds.db`.
4.  **Consumption:** The Agent accesses these DBs via Tools to answer user queries.

