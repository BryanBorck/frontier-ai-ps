import json
import os

import duckdb

DB_PATH = "src/infrastructure/database/br_funds.db"
OUTPUT_DIR = "src/infrastructure/database/extracted"


def extract_entities():
    try:
        conn = duckdb.connect(DB_PATH, read_only=True)

        print("=" * 80)
        print("EXTRACTING ENTITIES TO JSONL")
        print("=" * 80)

        # Query to get all service providers
        query = """
            SELECT service_providers
            FROM funds 
            WHERE service_providers IS NOT NULL 
            AND len(service_providers) > 0
        """

        results = conn.execute(query).fetchall()

        # Dictionaries to store unique entities by CNPJ (tax_id)
        # Structure: tax_id -> {name, count, variations}
        managers = {}
        custodians = {}
        administrators = {}
        controllers = {}

        for row in results:
            providers = row[0]
            for p in providers:
                name = p["name"]
                tax_id = p["tax_id"]
                role = p["type"]

                if not name or not tax_id:
                    continue

                name = name.strip().upper()

                target_dict = None
                if role == "MANAGER":
                    target_dict = managers
                elif role == "CUSTODIAN":
                    target_dict = custodians
                elif role == "ADMINISTRATOR":
                    target_dict = administrators
                elif role == "CONTROLLER":
                    target_dict = controllers

                if target_dict is not None:
                    if tax_id not in target_dict:
                        target_dict[tax_id] = {
                            "tax_id": tax_id,
                            "primary_name": name,
                            "count": 0,
                            "name_variations": set(),
                        }

                    target_dict[tax_id]["count"] += 1
                    target_dict[tax_id]["name_variations"].add(name)

                    # Update primary name if this one is longer (usually more descriptive)
                    if len(name) > len(target_dict[tax_id]["primary_name"]):
                        target_dict[tax_id]["primary_name"] = name

        # Helper function to save dict to JSONL
        def save_to_jsonl(data_dict, filename):
            filepath = os.path.join(OUTPUT_DIR, filename)
            print(f"Saving {len(data_dict)} records to {filepath}...")

            # Sort by count descending
            sorted_items = sorted(data_dict.values(), key=lambda x: x["count"], reverse=True)

            with open(filepath, "w", encoding="utf-8") as f:
                for item in sorted_items:
                    # Convert set to list for JSON serialization
                    item["name_variations"] = list(item["name_variations"])
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

        save_to_jsonl(managers, "managers.jsonl")
        save_to_jsonl(custodians, "custodians.jsonl")
        save_to_jsonl(administrators, "administrators.jsonl")
        # save_to_jsonl(controllers, "controllers.jsonl") # Optional if needed

        conn.close()
        print("\nExtraction complete!")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    extract_entities()
