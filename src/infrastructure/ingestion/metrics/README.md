# Fund Metrics Calculation

This directory contains scripts to calculate risk and performance metrics for investment funds.

## Ingestion Logic
- **Input:** `br_funds.db` (Fund Daily Snapshots) and `benchmarks.db` (IBOVESPA, etc.)
- **Output:** `fund_metrics` table in `br_funds.db` (persisted).

## Computed Metrics
- **Total Return (12m):** Cumulative return over the last 1 year.
- **Volatility (Annualized):** Standard deviation of daily returns * sqrt(252).
- **Sharpe Ratio:** Excess return over Risk-Free Rate / Volatility.
- **Beta:** Sensitivity to Market (IBOVESPA).
- **Correlation:** Correlation with Market.

## Usage
```bash
uv run src/infrastructure/ingestion/metrics/calculate_metrics.py
```

