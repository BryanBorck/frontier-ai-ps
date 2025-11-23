import glob
import os
import zipfile
from datetime import datetime
from io import BytesIO

import duckdb
import requests

# Configuration
BASE_URL_RECENT = "https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/"
BASE_URL_HIST = "https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/HIST/"
DOWNLOAD_DIR = "src/infrastructure/ingestion/cvm/lamina/data"
DB_PATH = "src/infrastructure/database/cvm_lamina.db"

# Ranges
START_DATE_HIST = datetime(2014, 1, 1)
END_DATE_HIST = datetime(2018, 12, 31)
START_DATE_RECENT = datetime(2019, 1, 1)
END_DATE_RECENT = datetime(2025, 12, 31)


def get_months_in_range(start_date, end_date):
    current = start_date
    dates = []
    while current <= end_date and current <= datetime.now():
        dates.append(current.strftime("%Y%m"))
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
    return dates


def download_file(url, target_dir, filename):
    if os.path.exists(target_dir) and glob.glob(os.path.join(target_dir, "*.csv")):
        return True
    print(f"Downloading {url}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 404:
            print(f"File not found: {filename}")
            return False
        response.raise_for_status()
        os.makedirs(target_dir, exist_ok=True)
        try:
            with zipfile.ZipFile(BytesIO(response.content)) as z:
                for member in z.namelist():
                    if (
                        "lamina_fi" in member
                        and "carteira" not in member
                        and "rentab" not in member
                        and member.endswith(".csv")
                    ):
                        z.extract(member, target_dir)
        except zipfile.BadZipFile:
            return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def ingest_to_duckdb():
    conn = duckdb.connect(DB_PATH)

    # 1. Gather all files
    all_files = glob.glob(f"{DOWNLOAD_DIR}/**/*.csv", recursive=True)
    # Filter for 2019-2025
    lamina_files = sorted(
        [
            f
            for f in all_files
            if "carteira" not in f
            and "rentab" not in f
            and (
                "lamina_fi_2025" in f
                or "lamina_fi_2024" in f
                or "lamina_fi_2023" in f
                or "lamina_fi_2022" in f
                or "lamina_fi_2021" in f
                or "lamina_fi_2020" in f
                or "lamina_fi_2019" in f
            )
        ],
        reverse=True,
    )

    if not lamina_files:
        print("No CSV files found.")
        return

    print(f"Found {len(lamina_files)} files. Starting DuckDB Ingestion with Schema Mapping...")

    conn.execute("DROP TABLE IF EXISTS raw_laminas")

    # 2. Create Table from Latest File (The "Gold Standard" - 2025 Schema)
    latest_file = lamina_files[0]
    print(f"Creating base schema from: {os.path.basename(latest_file)}")

    try:
        conn.execute(
            f"CREATE TABLE raw_laminas AS SELECT * FROM read_csv_auto('{latest_file}', encoding='latin-1') LIMIT 0"
        )
    except Exception:
        conn.execute(
            f"CREATE TABLE raw_laminas AS SELECT * FROM read_csv_auto('{latest_file}', encoding='utf-8') LIMIT 0"
        )

    conn.execute("ALTER TABLE raw_laminas ADD COLUMN filename VARCHAR")

    success_count = 0
    fail_count = 0

    # 3. Iterate and Append
    for csv_file in lamina_files:
        file_name = os.path.basename(csv_file)

        # Strategy: Try standard insert, then try legacy mapping (CNPJ_FUNDO -> CNPJ_FUNDO_CLASSE)
        # Encodings to try
        encodings = ["latin-1", "cp1252", "utf-8"]

        inserted = False
        for enc in encodings:
            # Attempt 1: Standard Insert (BY NAME)
            try:
                conn.execute(f"""
                    INSERT INTO raw_laminas BY NAME
                    SELECT *, '{file_name}' as filename 
                    FROM read_csv_auto('{csv_file}', encoding='{enc}', union_by_name=True, ignore_errors=True)
                """)
                inserted = True
                break
            except Exception as e:
                # Check if it's the specific column error
                if "CNPJ_FUNDO" in str(e) and "CNPJ_FUNDO_CLASSE" in str(e):
                    # Attempt 2: Legacy Mapping Insert
                    try:
                        conn.execute(f"""
                            INSERT INTO raw_laminas BY NAME
                            SELECT * REPLACE (CNPJ_FUNDO AS CNPJ_FUNDO_CLASSE), '{file_name}' as filename 
                            FROM read_csv_auto('{csv_file}', encoding='{enc}', union_by_name=True, ignore_errors=True)
                        """)
                        inserted = True
                        break
                    except Exception:
                        # print(f"  Legacy mapping failed for {file_name} ({enc}): {e2}")
                        pass  # Continue to next encoding
                else:
                    pass  # Not a schema error, maybe encoding

        if inserted:
            success_count += 1
        else:
            print(f"Failed {file_name}")
            fail_count += 1

    print(f"Ingestion Finished: {success_count} success, {fail_count} failed.")

    # 4. Deduplicate
    print("Deduplicating...")
    conn.execute("DROP TABLE IF EXISTS laminas")
    conn.execute("""
        CREATE TABLE laminas AS
        SELECT * EXCLUDE (filename)
        FROM raw_laminas
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY CNPJ_FUNDO_CLASSE 
            ORDER BY DT_COMPTC DESC, filename DESC
        ) = 1
    """)

    count = conn.execute("SELECT COUNT(*) FROM laminas").fetchone()[0]
    print(f"Final Count: {count} unique funds.")
    conn.close()


def main():
    # Ingest
    ingest_to_duckdb()


if __name__ == "__main__":
    main()
