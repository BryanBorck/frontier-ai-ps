import duckdb
import pandas as pd
import numpy as np

# Paths
FUNDS_DB = "src/infrastructure/database/br_funds.db"
BENCHMARKS_DB = "src/infrastructure/database/benchmarks.db"

def calculate_metrics():
    print("Starting Metrics Calculation Engine...")
    
    # 1. Connect and Attach
    conn = duckdb.connect(FUNDS_DB)
    conn.execute(f"ATTACH '{BENCHMARKS_DB}' AS benchmarks_db")
    
    # 2. Prepare Benchmarks (IBOVESPA)
    # Calculate daily returns for benchmark
    print("Preparing Benchmark Data...")
    bench_query = """
        WITH bench_daily AS (
            SELECT 
                date, 
                value,
                (value / LAG(value) OVER (ORDER BY date) - 1) as daily_return
            FROM benchmarks_db.benchmarks
            WHERE symbol = 'IBOVESPA'
        )
        SELECT date, daily_return as market_return 
        FROM bench_daily 
        WHERE daily_return IS NOT NULL
    """
    bench_df = conn.execute(bench_query).fetchdf()
    bench_df['date'] = pd.to_datetime(bench_df['date'])
    bench_df = bench_df.set_index('date')
    
    # 3. Prepare Fund Data (Daily Returns)
    # We process in chunks or per fund to avoid memory issues if dataset is huge.
    # For 60k funds, getting ALL daily returns might be heavy (10M rows).
    # DuckDB handles large data well, but pandas merge might lag. 
    # Let's try to do most heavy lifting in SQL.
    
    print("Calculating Daily Returns for Funds...")
    # We use fund_snapshots. timestamp is ISO string, need to cast to DATE
    # share_price is STRUCT(value, currency).
    
    # Create a temp table for fund returns
    conn.execute("DROP TABLE IF EXISTS fund_returns")
    conn.execute("""
        CREATE TEMP TABLE fund_returns AS
        WITH ordered_snaps AS (
            SELECT 
                fund_id.value as fund_uuid,
                CAST(timestamp AS DATE) as date,
                share_price.value as price
            FROM fund_snapshots
            WHERE price IS NOT NULL AND price > 0
        ),
        calc_ret AS (
            SELECT 
                fund_uuid,
                date,
                (price / LAG(price) OVER (PARTITION BY fund_uuid ORDER BY date) - 1) as daily_return
            FROM ordered_snaps
        )
        SELECT * FROM calc_ret WHERE daily_return IS NOT NULL
    """)
    
    # 4. Aggregate Metrics (Window: 12 Months)
    # We'll calculate for the last available year of data for each fund
    # For Sharpe, we assume Risk Free Rate = 10% p.a. roughly = 0.000378 daily (since we don't have CDI series yet)
    RISK_FREE_DAILY = 0.000378
    TRADING_DAYS = 252
    
    print("Aggregating Volatility and Returns (DuckDB)...")
    
    # Volatility & Returns
    # Filter for last 12 months relative to the max date in DB (or per fund?)
    # Let's take the global max date to define "current"
    max_date = conn.execute("SELECT MAX(date) FROM fund_returns").fetchone()[0]
    cutoff_date = max_date - timedelta(days=365)
    
    conn.execute(f"DROP TABLE IF EXISTS fund_metrics")
    
    query_metrics = f"""
        CREATE TABLE fund_metrics AS
        WITH filtered AS (
            SELECT * FROM fund_returns WHERE date >= '{cutoff_date}'
        ),
        stats AS (
            SELECT 
                fund_uuid,
                COUNT(*) as obs,
                STDDEV(daily_return) as vol_daily,
                AVG(daily_return) as mean_return_daily,
                (PRODUCT(1 + daily_return) - 1) as total_return_12m
            FROM filtered
            GROUP BY fund_uuid
            HAVING obs > 100 -- Minimum observations to be statistically relevant
        )
        SELECT 
            fund_uuid,
            obs as observations,
            total_return_12m,
            vol_daily * SQRT({TRADING_DAYS}) as volatility_annualized,
            (mean_return_daily - {RISK_FREE_DAILY}) / NULLIF(vol_daily, 0) * SQRT({TRADING_DAYS}) as sharpe_ratio
        FROM stats
    """
    conn.execute(query_metrics)
    
    # 5. Calculate Beta (Requires joining with Benchmark)
    # Since DuckDB correlation might be tricky with different calendars, 
    # we'll do a Python join for the funds that passed the filter.
    # For 60k funds, this Python loop might be slow. 
    # Optimized approach: Groupby Apply in Pandas on the filtered set.
    
    print("Calculating Beta and Correlation (Pandas)...")
    
    # Get daily returns for funds that are in our metrics table
    funds_subset_query = f"""
        SELECT r.fund_uuid, r.date, r.daily_return
        FROM fund_returns r
        JOIN fund_metrics m ON r.fund_uuid = m.fund_uuid
        WHERE r.date >= '{cutoff_date}'
    """
    funds_df = conn.execute(funds_subset_query).fetchdf()
    funds_df['date'] = pd.to_datetime(funds_df['date'])
    
    # Merge with Benchmark
    merged = pd.merge(funds_df, bench_df, on='date', how='inner')
    
    # Function to calc beta/corr
    def calc_risk_metrics(g):
        if len(g) < 50: return pd.Series({'beta': None, 'correlation': None})
        cov = np.cov(g['daily_return'], g['market_return'])[0][1]
        var_market = np.var(g['market_return'])
        beta = cov / var_market if var_market != 0 else 0
        corr = g['daily_return'].corr(g['market_return'])
        return pd.Series({'beta': beta, 'correlation': corr})

    risk_metrics = merged.groupby('fund_uuid').apply(calc_risk_metrics).reset_index()
    
    # 6. Update Metrics Table with Python results
    # Create temp table for risk metrics
    conn.execute("CREATE TEMP TABLE risk_metrics_py (fund_uuid VARCHAR, beta DOUBLE, correlation DOUBLE)")
    conn.execute("INSERT INTO risk_metrics_py SELECT * FROM risk_metrics")
    
    # Add columns to main table
    try:
        conn.execute("ALTER TABLE fund_metrics ADD COLUMN beta DOUBLE")
        conn.execute("ALTER TABLE fund_metrics ADD COLUMN correlation DOUBLE")
    except:
        pass # columns might exist
        
    # Update
    conn.execute("""
        UPDATE fund_metrics
        SET beta = r.beta, correlation = r.correlation
        FROM risk_metrics_py r
        WHERE fund_metrics.fund_uuid = r.fund_uuid
    """)
    
    # 7. Final Review
    print("\n--- Metrics Calculation Complete ---")
    summary = conn.execute("SELECT * FROM fund_metrics ORDER BY sharpe_ratio DESC LIMIT 5").fetchdf()
    pd.set_option('display.max_columns', None)
    print(summary)
    
    count = conn.execute("SELECT COUNT(*) FROM fund_metrics").fetchone()[0]
    print(f"Calculated metrics for {count} funds.")
    
    conn.execute("DETACH benchmarks_db")
    conn.close()

from datetime import timedelta

if __name__ == "__main__":
    calculate_metrics()

