import glob
import os
import zipfile
from datetime import datetime
from io import BytesIO

import duckdb
import requests


class CVMDataIngestor:
    """
    Ingests CVM Lamina data (funds daily info) into DuckDB.
    """

    BASE_URL_RECENT = "https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/"
    BASE_URL_HIST = "https://dados.cvm.gov.br/dados/FI/DOC/LAMINA/DADOS/HIST/"

    def __init__(self, download_dir: str, db_path: str):
        self.download_dir = download_dir
        self.db_path = db_path

    def download_file(self, url: str, filename: str) -> bool:
        """Download a single file if not exists."""
        target_dir = os.path.join(self.download_dir, filename.replace(".csv", ""))
        # Simple check: if we have CSVs in the dir, assume downloaded
        # This logic matches the original script but could be robustified
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
                        # Filter for interesting CSVs
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
            print(f"Error downloading {url}: {e}")
            return False

    def ingest(self):
        """Main ingestion process."""
        conn = duckdb.connect(self.db_path)

        # 1. Gather all files
        all_files = glob.glob(f"{self.download_dir}/**/*.csv", recursive=True)
        # Filter for recent years (2019-2025 as per original script logic)
        # Ideally this should be configurable or dynamic
        lamina_files = sorted(
            [
                f
                for f in all_files
                if "carteira" not in f
                and "rentab" not in f
                and any(f"lamina_fi_{year}" in f for year in range(2019, 2026))
            ],
            reverse=True,
        )

        if not lamina_files:
            print("No CSV files found.")
            return

        print(
            f"Found {len(lamina_files)} files. Starting DuckDB Ingestion with Schema Mapping..."
        )

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
            encodings = ["latin-1", "cp1252", "utf-8"]
            inserted = False

            for enc in encodings:
                try:
                    conn.execute(f"""
                        INSERT INTO raw_laminas BY NAME
                        SELECT *, '{file_name}' as filename 
                        FROM read_csv_auto('{csv_file}', encoding='{enc}', union_by_name=True, ignore_errors=True)
                    """)
                    inserted = True
                    break
                except Exception as e:
                    if "CNPJ_FUNDO" in str(e) and "CNPJ_FUNDO_CLASSE" in str(e):
                        try:
                            conn.execute(f"""
                                INSERT INTO raw_laminas BY NAME
                                SELECT * REPLACE (CNPJ_FUNDO AS CNPJ_FUNDO_CLASSE), '{file_name}' as filename 
                                FROM read_csv_auto('{csv_file}', encoding='{enc}', union_by_name=True, ignore_errors=True)
                            """)
                            inserted = True
                            break
                        except Exception:
                            pass
                    else:
                        pass

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

