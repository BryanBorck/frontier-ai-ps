# Exa Web Search Tool

AI-powered web search tool using [Exa AI](https://exa.ai) for high-quality, semantically relevant search results.

## Features

- **AI-Powered Search**: Leverages Exa's neural search technology for semantic understanding
- **Autoprompt**: Automatically optimizes queries for better results
- **Content Extraction**: Optional extraction of page text and highlighted snippets
- **ReAct Agent Compatible**: Designed for integration with DSPy ReAct agents
- **Type-Safe**: Built with Pydantic models for robust data validation

## Installation

1. Install the Exa Python SDK:

```bash
uv pip install exa-py
```

2. Set your Exa API key:

```bash
export EXA_API_KEY="your-api-key-here"
```

Get your API key at [exa.ai](https://exa.ai)

## Usage

### Public Interface

Use the `tool_web_search` function for standalone usage:

```python
from src.tools.tool_web_search import tool_web_search

# Basic search
results = tool_web_search({
    "query": "latest AI research papers",
    "num_results": 5
})

# Advanced search with content
results = tool_web_search({
    "query": "Python async programming best practices",
    "num_results": 10,
    "include_text": True,
    "include_highlights": True,
    "use_autoprompt": True
})

# Process results
for result in results:
    print(f"{result['title']}")
    print(f"URL: {result['url']}")
    print(f"Score: {result['score']}")
    if 'text' in result:
        print(f"Content preview: {result['text'][:200]}...")
    print()
```

### ReAct Agent Integration

Use the `_ExaSearchInternal` class for DSPy ReAct agents:

```python
from src.tools.tool_web_search import _ExaSearchInternal
import dspy

# Initialize tools
exa_searcher = _ExaSearchInternal()

# Create ReAct agent with Exa search capability
agent = dspy.ReAct(
    signature="question -> answer",
    tools=[exa_searcher.search],
    max_iters=5
)

# The agent can now use web search
response = agent(question="What are the latest developments in quantum computing?")
```

## Parameters

### Input Parameters

| Parameter            | Type    | Required | Default | Description                             |
| -------------------- | ------- | -------- | ------- | --------------------------------------- |
| `query`              | string  | Yes      | -       | The search query to execute             |
| `num_results`        | integer | No       | 10      | Maximum number of results to return     |
| `include_text`       | boolean | No       | true    | Whether to include page text content    |
| `include_highlights` | boolean | No       | false   | Whether to include highlighted snippets |
| `use_autoprompt`     | boolean | No       | true    | Whether to use Exa's autoprompt feature |

### Output Schema

Each result contains:

| Field            | Type   | Description                                         |
| ---------------- | ------ | --------------------------------------------------- |
| `title`          | string | Page title                                          |
| `url`            | string | Page URL                                            |
| `score`          | number | Relevance score from Exa                            |
| `published_date` | string | Publication date (if available)                     |
| `author`         | string | Author (if available)                               |
| `text`           | string | Page content (if `include_text=true`)               |
| `highlights`     | array  | Highlighted snippets (if `include_highlights=true`) |

## Testing

Run the test suite:

```bash
# Unit tests (basic functionality, no API calls)
uv run python -m pytest src/tools/tool_web_search/tests/test_unit.py

# Integration tests (requires EXA_API_KEY)
export EXA_API_KEY="your-api-key"
uv run python -m pytest src/tools/tool_web_search/tests/test_integration.py

# All tests
uv run python -m pytest src/tools/tool_web_search/tests/
```

## Examples

### Example 1: Research Assistant

```python
# Search for academic papers
results = tool_web_search({
    "query": "transformer architecture attention mechanisms research papers",
    "num_results": 5,
    "include_text": True,
    "use_autoprompt": True
})

for paper in results:
    print(f"📄 {paper['title']}")
    print(f"🔗 {paper['url']}")
    if paper.get('published_date'):
        print(f"📅 {paper['published_date']}")
```

### Example 2: Technical Documentation Search

```python
# Find documentation for a specific technology
results = tool_web_search({
    "query": "how to implement OAuth2 authentication in FastAPI",
    "num_results": 3,
    "include_text": True
})
```

### Example 3: News and Updates

```python
# Get recent news about a topic
results = tool_web_search({
    "query": "latest developments in artificial intelligence 2024",
    "num_results": 10,
    "include_highlights": True
})
```

## Error Handling

The tool raises clear exceptions for common issues:

```python
from src.tools.tool_web_search import tool_web_search

try:
    results = tool_web_search({
        "query": "test query"
    })
except ValueError as e:
    # Missing required fields or API key not set
    print(f"Configuration error: {e}")
except Exception as e:
    # API errors or network issues
    print(f"Search failed: {e}")
```

## Architecture

Following the standard tool pattern:

```
tool_web_search/
├── __init__.py           # Package exports
├── index.py              # Public function + Internal class
├── schema.py             # Schema loader
├── schema.json           # Tool metadata
├── module_pipeline.py    # Core Exa API logic
├── README.md            # This file
└── tests/
    ├── test_unit.py     # Unit tests
    └── test_integration.py  # Integration tests
```

## Notes

- **API Key**: Required for all operations. Get one at [exa.ai](https://exa.ai)
- **Rate Limits**: Exa API has rate limits based on your plan
- **Autoprompt**: Enabled by default for better query optimization
- **Content Extraction**: Set `include_text=False` for faster responses when only metadata is needed
- **Portuguese Support**: Exa handles multilingual queries, including Portuguese

## Related Tools

- `tool_semantic_search`: Semantic search over local fund database
- `tool_search_db`: Structured database search
- `tool_parse_query`: Query parsing and parameter extraction
