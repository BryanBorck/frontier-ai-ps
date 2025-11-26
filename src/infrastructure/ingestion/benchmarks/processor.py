import duckdb
import pandas as pd
import requests
import yfinance as yf
from io import StringIO


class BenchmarkIngestor:
    """
    Ingests Benchmark data (CDI, SELIC, IBOVESPA) into DuckDB.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def fetch_bcb_series(self, code, start_date="01/01/2015") -> pd.DataFrame:
        """
        Fetches time series from Banco Central do Brasil (BCB) API.
        """
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=csv&dataInicial={start_date}"
        print(f"Fetching BCB Series {code}...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=30)
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

    def fetch_yahoo_series(self, ticker, start_date="2000-01-01") -> pd.DataFrame:
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

    def ingest(self):
        """Main ingestion process."""
        # 1. Fetch Data
        cdi_daily = self.fetch_bcb_series(12, "01/01/2015")
        if not cdi_daily.empty:
            cdi_daily["symbol"] = "CDI_DAILY_PCT"

        selic_daily = self.fetch_bcb_series(11, "01/01/2015")
        if not selic_daily.empty:
            selic_daily["symbol"] = "SELIC_DAILY_PCT"

        ibov = self.fetch_yahoo_series("^BVSP", "2015-01-01")
        if not ibov.empty:
            ibov["symbol"] = "IBOVESPA"

        # Combine
        all_data = pd.concat([cdi_daily, selic_daily, ibov], ignore_index=True)

        if all_data.empty:
            print("No data fetched.")
            return

        print(f"Fetched {len(all_data)} rows total.")

        # 2. Ingest to DuckDB
        conn = duckdb.connect(self.db_path)

        print("Ingesting to DuckDB...")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS benchmarks (date DATE, symbol VARCHAR, value DOUBLE)"
        )

        # Clear existing to avoid dupes (simple strategy for now)
        conn.execute("DELETE FROM benchmarks")

        conn.execute("INSERT INTO benchmarks SELECT date, symbol, value FROM all_data")

        # 3. Verify
        count = conn.execute("SELECT COUNT(*) FROM benchmarks").fetchone()[0]
        print(f"Total rows in DB: {count}")

        conn.close()

