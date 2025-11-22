"""Schema definitions for tool_search_db."""

import json
from pathlib import Path

# Load schema from JSON file
_schema_path = Path(__file__).parent / "schema.json"
with open(_schema_path) as f:
    TOOL_SCHEMA = json.load(f)

TOOL_NAME = TOOL_SCHEMA["tool_name"]
TOOL_DESCRIPTION = TOOL_SCHEMA["description"]
INPUT_SCHEMA = TOOL_SCHEMA["input_schema"]
OUTPUT_SCHEMA = TOOL_SCHEMA["output_schema"]
