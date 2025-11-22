"""Schema definitions for tool_parse_query."""

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

# Fund type enum
FUND_TYPES = OUTPUT_SCHEMA["fund_type"]["enum"]

# Investment class enum
INVESTMENT_CLASSES = OUTPUT_SCHEMA["investment_class"]["enum"]
