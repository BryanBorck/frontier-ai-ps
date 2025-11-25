"""
Schema definition for the Exa web search tool.

This module loads the schema from schema.json and exposes it as Python constants.
"""

import json
from pathlib import Path

# Load schema from JSON file
_schema_path = Path(__file__).parent / "schema.json"
with open(_schema_path) as f:
    TOOL_SCHEMA = json.load(f)

# Export schema components as constants
TOOL_NAME = TOOL_SCHEMA["tool_name"]
TOOL_DESCRIPTION = TOOL_SCHEMA["description"]
INPUT_SCHEMA = TOOL_SCHEMA["input_schema"]
OUTPUT_SCHEMA = TOOL_SCHEMA["output_schema"]
