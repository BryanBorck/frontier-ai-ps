# Tool: Parse Fund Query

## Purpose
This tool parses a user's natural language query about Brazilian investment funds and extracts structured search criteria including:
- `fund_legal_name`: The name of a specific fund (if mentioned)
- `fund_type`: The type of fund (FI, FIP, FIDC, FII, ETF, etc.)
- `investment_class`: The investment class (Multimercado, Ações, Renda Fixa, etc.)
- `fund_of_funds`: Whether the user wants fund-of-funds (if specified)

## When to use
Use this tool when your agent receives a user query about Brazilian funds that needs to be converted into structured criteria for database search. For example:
- "find FIP funds" → `{fund_type: "FIP"}`
- "show me funds with BTG in the name" → `{fund_legal_name: "BTG"}`
- "Multimercado funds" → `{investment_class: "Multimercado"}`

## Input
Schema defined in `schema.json` — expects `query: string`.

**Example:**
```json
{
  "query": "find FIP funds with Vinci in the name"
}
```

## Output
Schema defined in `schema.json` — returns all four criteria fields (nullable).

**Example output:**
```json
{
  "fund_legal_name": "Vinci",
  "fund_type": "FIP",
  "investment_class": null,
  "fund_of_funds": null
}
```

## Edge cases & Constraints
- If the user query doesn't mention a specific criterion, it will be `null`
- Fund type extraction is based on common Brazilian fund types: FI, FIP, FIDC, FII, ETF
- Investment class extraction recognizes: Multimercado, Ações, Renda Fixa, Cambial, FIP, Dívida Externa, Imobiliário
- The tool only extracts information explicitly mentioned or clearly implied in the query
- If multiple funds are mentioned, currently returns the primary one

## Usage

### As a standalone tool
```python
from src.tools.tool_parse_query.index import tool_parse_query

result = tool_parse_query({"query": "find FIP funds"})
# Returns: {"fund_legal_name": null, "fund_type": "FIP", ...}
```

### Using the parser class
```python
from src.tools.tool_parse_query.index import FundQueryParser

parser = FundQueryParser()
criteria = parser.parse("show me Multimercado funds")
# Returns FundSearchCriteria object
```

### With DSPy ReAct agent
```python
import dspy
from src.tools.tool_parse_query.index import FundQueryParser

parser = FundQueryParser()
agent = dspy.ReAct(
    signature="question -> answer",
    tools=[parser.parse, ...],
    max_iters=5
)
```

## Testing
See tests in `tests/test_unit.py` and `tests/test_integration.py`.

Run tests:
```bash
pytest src/tools/tool_parse_query/tests/
```

## Optimization
This tool uses DSPy's Predict module and can be optimized using DSPy's optimizer framework:
1. Collect example queries with correct extracted criteria
2. Use DSPy optimizers (e.g., BootstrapFewShot) to improve extraction accuracy
3. The module pipeline is designed to be optimizable - see `module_pipeline.py`

## Architecture
- `index.py`: Main entry point with `tool_parse_query()` function and `FundQueryParser` class
- `module_pipeline.py`: DSPy module definition and `execute()` function
- `schema.json`: JSON schema for input/output validation
- `README.md`: This documentation
- `tests/`: Unit and integration tests

## Dependencies
- DSPy: For LLM-based text extraction
- Pydantic: For structured output validation
