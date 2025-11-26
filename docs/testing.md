# Testing

## Test Structure

### 1. Unit Tests (`src/agent/fund_search/modules/tests/`)
- Test individual modules in isolation
- Mock DSPy LLM calls
- Fast (< 1s per test)
- Marker: `@pytest.mark.unit`

```python
def test_normalize_xp_variations():
    result = EntityMapper.normalize_provider("XP Investimentos")
    assert result is None or isinstance(result, str)
```

### 2. Integration Tests
- Test component interactions with real dependencies
- Real LLM calls + database queries
- Expensive (API costs)
- Marker: `@pytest.mark.integration`
- Most are skipped in favor of E2E tests

### 3. E2E Tests (`src/agent/fund_search/tests/e2e/`)
- Complete workflows: Query → Intent → Extraction → Search → Response
- Requires real databases
- Markers: `@pytest.mark.e2e`, `@pytest.mark.requires_db`, `@pytest.mark.slow`

**Key files**:
- `test_fund_search_flow.py` - User workflows
- `test_orchestrator_integration.py` - Pipeline tests
- `test_extraction_*.py` - Extraction E2E
- `test_search_*.py` - Search tools E2E

## Running Tests

```bash
# Unit tests
pytest src/agent/fund_search/modules/tests/ -v

# E2E tests (requires DB + API key)
pytest src/agent/fund_search/tests/e2e/ -v -m e2e

# Specific test
pytest src/agent/fund_search/tests/e2e/test_fund_search_flow.py -v

# Skip slow tests
pytest -m "not slow"
```

## Markers

- `@pytest.mark.unit` - Fast, mocked
- `@pytest.mark.integration` - Real dependencies, expensive
- `@pytest.mark.e2e` - Full workflow
- `@pytest.mark.requires_db` - Needs database
- `@pytest.mark.requires_llm` - Real LLM calls (very expensive)
- `@pytest.mark.slow` - Takes > 5 seconds

## Fixtures

Defined in `conftest.py`:
- `fund_search_tool` - Configured tool instance
- `real_db_path` - Database path
- `real_vector_store_path` - Vector store path
- `api_key` - OpenAI key from environment
