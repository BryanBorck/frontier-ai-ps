
# Fund Search Tests

Comprehensive test suite for the fund_search agent, organized by test type and scope.

## Directory Structure

```
tests/
├── fixtures/              # Shared test data and database fixtures
│   ├── db_fixtures.py     # Database creation utilities
│   └── data/              # Static test data files
├── integration/           # Integration tests (multiple components)
│   └── test_search_manager.py
├── e2e/                   # End-to-end workflow tests
│   └── test_fund_search_flow.py
└── conftest.py            # Root fixtures and configuration
```

## Unit Tests (Co-located)

Unit tests live with the code they test:

- `tools/search_funds/tests/` - FundSearchTool unit tests
- `tools/search_positions/tests/` - PositionSearchTool unit tests
- `tools/search_semantic/tests/` - SemanticSearchTool unit tests
- `tools/search_snapshots/tests/` - SnapshotSearchTool unit tests
- `tools/search_performance/tests/` - PerformanceSearchTool unit tests
- `modules/tests/` - Module unit tests (intent, extraction, etc.)

## Test Types and Markers

### Markers

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Fast unit tests with mocked data (< 100ms)
- `@pytest.mark.integration` - Integration tests with real DB snapshots
- `@pytest.mark.e2e` - End-to-end workflow tests
- `@pytest.mark.slow` - Tests that take > 1 second
- `@pytest.mark.requires_db` - Tests requiring real database files
- `@pytest.mark.requires_llm` - Tests making actual LLM API calls (expensive)

### Running Tests Selectively

```bash
# All tests
pytest src/agent/fund_search/

# Unit tests only (fast, no DB required)
pytest src/agent/fund_search/ -m unit

# Integration tests (requires DB)
pytest src/agent/fund_search/ -m integration

# E2E tests (requires DB, slow)
pytest src/agent/fund_search/ -m e2e

# Everything except expensive LLM tests
pytest src/agent/fund_search/ -m "not requires_llm"

# Only tests for a specific tool
pytest src/agent/fund_search/tools/search_funds/tests/

# Fast tests during development
pytest src/agent/fund_search/ -m "unit and not slow"

# Integration + E2E (full validation)
pytest src/agent/fund_search/ -m "integration or e2e"
```

## Database Strategy

### Unit Tests → Mock DBs
- Use `mock_db_path` fixture
- Simple, minimal schema
- Fast creation (milliseconds)
- Predictable, isolated data

### Integration Tests → DB Snapshots
- Use `db_snapshot` and `vector_store_snapshot` fixtures
- Copy of real database
- Real schema and representative data
- Test actual SQL queries and embeddings
- No risk of corrupting production DB

### E2E Tests → Real DB (Read-Only)
- Use `real_db_path` and `real_vector_store_path` fixtures
- Point to actual database files
- Test with production data
- Validate real-world scenarios

## Fixtures

### Root Fixtures (tests/conftest.py)

- `real_db_path` - Path to production database
- `real_vector_store_path` - Path to vector store
- `db_snapshot` - Temporary copy of real DB
- `vector_store_snapshot` - Temporary copy of vector store
- `mock_db_path` - Simple mock database for unit tests
- `sample_fund_results` - Sample fund data
- `mock_llm_response` - Mock LLM responses (avoid API calls)
- `disable_mlflow` - Auto-disable MLflow tracing in tests

### Tool-Specific Fixtures

Each tool has its own `conftest.py` with specialized fixtures.

## Test Coverage Goals

### Unit Tests (Minimum)
- ✅ All search tools (5 tools)
- ✅ All modules (intent, extraction, normalization, manager)
- Target: > 80% line coverage

### Integration Tests
- ✅ SearchManager orchestration
- ✅ Tool interactions
- Multi-turn conversation flows
- Target: Critical paths covered

### E2E Tests
- ✅ Complete user journeys
- ✅ Real data scenarios
- Edge cases and error handling
- Target: Major workflows validated

## Adding New Tests

### 1. Unit Test (New Tool)

```python
# src/agent/fund_search/tools/my_tool/tests/test_unit.py

import pytest
from ..tool import MyTool

@pytest.mark.unit
class TestMyTool:
    def test_basic_functionality(self, mock_db_path):
        tool = MyTool(db_path=mock_db_path)
        result = tool.forward(...)
        assert result is not None
```

### 2. Integration Test

```python
# src/agent/fund_search/tests/integration/test_my_integration.py

import pytest

@pytest.mark.integration
@pytest.mark.requires_db
class TestMyIntegration:
    def test_with_real_data(self, db_snapshot):
        # Test using real database snapshot
        pass
```

### 3. E2E Test

```python
# src/agent/fund_search/tests/e2e/test_my_workflow.py

import pytest

@pytest.mark.e2e
@pytest.mark.requires_db
@pytest.mark.slow
class TestMyWorkflow:
    def test_complete_flow(self, real_db_path):
        # Test complete user journey
        pass
```

## Continuous Integration

Recommended CI test stages:

1. **Fast (< 1 min)**: Unit tests only
   ```bash
   pytest -m unit
   ```

2. **Medium (< 5 min)**: Unit + Integration (mocked LLM)
   ```bash
   pytest -m "unit or integration" -m "not requires_llm"
   ```

3. **Full (< 15 min)**: Everything except expensive LLM tests
   ```bash
   pytest -m "not requires_llm"
   ```

4. **Nightly**: Full suite including LLM tests
   ```bash
   pytest
   ```

## Known Issues / TODOs

- [ ] Add property-based tests for query parsing
- [ ] Add performance benchmarks
- [ ] Increase coverage for error scenarios
- [ ] Add tests for edge cases in multi-turn conversations
- [ ] Mock external dependencies more thoroughly
- [ ] Add snapshot testing for complex outputs

## Contributing

When adding new features:

1. Write unit tests first (TDD)
2. Add integration tests for multi-component interactions
3. Add E2E test for new user-facing workflows
4. Update this README if adding new test categories
5. Ensure all tests pass before committing

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Database Schema](../../infrastructure/database/README.md)
- [DSPy Testing Guide](https://dspy-docs.vercel.app/docs/building-blocks/testing)
