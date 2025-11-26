import json
from pathlib import Path


def update_dataset(file_path):
    print(f"Updating {file_path}...")
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {path}")
        return

    new_lines = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)

            # Check for informational intent
            if "informational" in data.get("expected_intents", []):
                query = data["query"]
                # Remap logic
                new_intent = ["general_browse"]

                # For specific definitions, we might want find_by_strategy or find_by_criteria if we want to search
                # But for now, let's map all conversational/info to general_browse as per recent signature update
                # "Conversational queries ... should be mapped to general_browse"

                data["expected_intents"] = new_intent

                # Update category if needed, but keeping it is fine for analysis
                # print(f"  Remapped '{query}' from informational to {new_intent}")

            new_lines.append(json.dumps(data))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")
    print(f"Done updating {file_path}")


if __name__ == "__main__":
    base_dir = "src/evaluation/data"
    files = [
        f"{base_dir}/fund_search_evaluation.jsonl",
        f"{base_dir}/fund_search_evaluation_enriched.jsonl",
    ]

    for file in files:
        update_dataset(file)
