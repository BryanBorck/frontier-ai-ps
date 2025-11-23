import duckdb
import pandas as pd
import requests
import yfinance as yf

# Configuration
DB_PATH = "src/infrastructure/database/benchmarks.db"
DATA_DIR = "src/infrastructure/ingestion/benchmarks/data"


def fetch_bcb_series(code, start_date="01/01/2015"):
    """
    Fetches time series from Banco Central do Brasil (BCB) API.
    Code 12 = CDI (Interest Rate) - annualized daily rate? No, 12 is 'Taxa de juros - CDI'.
    Actually, for daily returns to calculate performance, we usually want the accumulated index or the daily factor.

    Common codes:
    - 12: CDI - % a.d. (percent per day) or % a.a.?
      Code 12 is "Taxa de juros - CDI - % a.d." (daily percentage).
    - 4389: CDI accumulated (monthly).

    To calculate Sharpe, we need the Daily Risk Free Rate. Code 12 (CDI daily) is perfect.
    """
    # Try CSV format with requests to handle headers manually
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=csv&dataInicial={start_date}"
    print(f"Fetching BCB Series {code}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        from io import StringIO

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # BCB returns CSV with ; separator and , decimal
        df = pd.read_csv(StringIO(response.text), sep=";", decimal=",")
        # df columns are usually 'data' and 'valor'
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["valor"] = pd.to_numeric(df["valor"])
        df = df.rename(columns={"data": "date", "valor": "value"})
        return df
    except Exception as e:
        print(f"Error fetching BCB data: {e}")
        return pd.DataFrame()


def fetch_yahoo_series(ticker, start_date="2000-01-01"):
    """
    Fetches data from Yahoo Finance.
    """
    print(f"Fetching Yahoo Finance {ticker}...")
    try:
        # yfinance expects YYYY-MM-DD
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(start=start_date)
        df = df.reset_index()
        # yfinance returns Date with timezone, normalize to date only
        df["Date"] = df["Date"].dt.date
        df = df[["Date", "Close"]]
        df = df.rename(columns={"Date": "date", "Close": "value"})
        return df
    except Exception as e:
        print(f"Error fetching Yahoo data: {e}")
        return pd.DataFrame()


def ingest_benchmarks():
    # 1. Fetch Data
    # CDI (Daily rate in %)
    # BCB limits to 10 years per request. Fetching from 2015 is enough for now.
    cdi_daily = fetch_bcb_series(12, "01/01/2015")
    if not cdi_daily.empty:
        cdi_daily["symbol"] = "CDI_DAILY_PCT"

    # SELIC (Daily rate in %) - Code 11
    selic_daily = fetch_bcb_series(11, "01/01/2015")
    if not selic_daily.empty:
        selic_daily["symbol"] = "SELIC_DAILY_PCT"

    # IBOVESPA
    ibov = fetch_yahoo_series("^BVSP", "2015-01-01")  # Yahoo keeps YYYY-MM-DD
    if not ibov.empty:
        ibov["symbol"] = "IBOVESPA"

    # IFIX (Real Estate)
    ifix = fetch_yahoo_series("IFIX.SA")  # Yahoo uses IFIX.SA for some, or maybe not available.
    # Attempting IFIX.SA often fails or is delayed. Let's stick to IBOV for now.

    # Combine
    all_data = pd.concat([cdi_daily, selic_daily, ibov], ignore_index=True)

    if all_data.empty:
        print("No data fetched.")
        return

    print(f"Fetched {len(all_data)} rows total.")

    # 2. Ingest to DuckDB
    conn = duckdb.connect(DB_PATH)

    print("Ingesting to DuckDB...")
    conn.execute("CREATE TABLE IF NOT EXISTS benchmarks (date DATE, symbol VARCHAR, value DOUBLE)")

    # Clear existing to avoid dupes (simple strategy for now)
    conn.execute("DELETE FROM benchmarks")

    conn.execute("INSERT INTO benchmarks SELECT date, symbol, value FROM all_data")

    # 3. Verify
    count = conn.execute("SELECT COUNT(*) FROM benchmarks").fetchone()[0]
    print(f"Total rows in DB: {count}")

    sample = conn.execute("SELECT * FROM benchmarks LIMIT 5").fetchdf()
    print(sample)

    conn.close()


if __name__ == "__main__":
    ingest_benchmarks()
