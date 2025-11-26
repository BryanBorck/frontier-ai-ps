# Testing Strategy Guide

## The Testing Pyramid

```
              /\
             /  \
            / E2E \          Few, Slow, Expensive
           /______.\         Test complete user workflows
          /        .\
         /          .\
        / Integration\       Some, Medium speed
       /_____________.\      Test components working together
      /               .\
     /                 .\
    /    Unit Tests     \    Many, Fast, Cheap
   /_____________________\   Test individual functions
```

## When to Use Each Test Type

### Unit Tests (Many, Fast)

**Use when:**
- Testing business logic in isolation
- Validating input parsing/validation
- Testing error handling
- Mocking external dependencies

**Example: search_funds unit test**
```python
def test_search_query_building():
    """Test that criteria builds correct WHERE clauses."""
    # Mock DB to test logic, not infrastructure
```

**Pros:**
- ⚡ Fast (milliseconds)
- 🎯 Pinpoint failures
- 🔒 Stable (no external dependencies)

**Cons:**
- ❌ Doesn't test real SQL execution
- ❌ Doesn't catch schema mismatches
- ❌ Doesn't validate actual data interactions

---

### Integration Tests (Some, Medium)

**Use when:**
- Testing SQL queries against real schema
- Validating complex data structures (STRUCT, arrays)
- Testing file I/O (loading configs, entity mappings)
- Testing multiple tools working together

**Example: search_funds integration test**
```python
def test_search_with_real_schema(db_snapshot):
    """Test queries work against actual database schema."""
    # Uses real DB snapshot - validates SQL actually works!
```

**Pros:**
- ✅ Catches schema mismatches
- ✅ Validates real SQL execution
- ✅ Tests actual data interactions
- ✅ Still fast enough for CI (seconds)

**Cons:**
- 🐌 Slower than unit tests
- 📦 Requires real/realistic data
- 🔧 More setup needed

---

### E2E Tests (Few, Slow)

**Use when:**
- Testing complete user workflows
- Validating business requirements
- Testing multi-step processes
- Smoke testing critical paths

**Example: fund_search E2E test**
```python
def test_complete_fund_search_workflow():
    """User searches for fund by name and gets results."""
    # Tests entire flow: query → intent → extraction → search → response
```

**Pros:**
- 🎭 Tests real user scenarios
- 🔍 Catches integration issues
- 📊 Validates business logic end-to-end

**Cons:**
- 🐢 Slowest (seconds to minutes)
- 💰 Expensive (LLM API calls)
- 🔍 Hard to debug (many components involved)

---

## Testing Strategy by Component

### 🔧 search_funds Tool

| Test Type | What to Test | Why |
|-----------|--------------|-----|
| **Unit** | Query building logic, parameter validation, error handling | Fast feedback on logic |
| **Integration** | SQL queries work on real schema, STRUCT access, entity mapping | Critical - complex SQL needs validation |

**Why both?**
- Unit tests verify the logic (e.g., "Does it build the right WHERE clause?")
- Integration tests verify it actually works (e.g., "Does DuckDB execute the query successfully?")

**Example scenario:**
```python
# Unit test - PASSES (logic is correct)
def test_builds_query_with_fund_type():
    # Verify it creates: "fund_type IN ('FII')"
    assert "fund_type IN" in query

# Integration test - FAILS (schema changed!)
def test_search_by_fund_type_real_db():
    # Runs actual query against DB
    results = tool.forward(criteria)  # ❌ Error: column 'fund_type' not found!
```

### 🔧 search_semantic Tool

| Test Type | What to Test | Why |
|-----------|--------------|-----|
| **Unit** | Basic initialization, parameter handling | Smoke tests |
| **Integration** | Semantic similarity with real embeddings | CRITICAL - can't mock vector math |

**Why mostly integration?**
- Vector similarity is impossible to mock meaningfully
- Need real embeddings to test semantic search
- Keyword boosting needs real fund names

### 🔧 search_positions Tool

| Test Type | What to Test | Why |
|-----------|--------------|-----|
| **Unit** | Query building, parameter validation | Fast feedback |
| **Integration** | Aggregations, joins with real data | SQL complexity needs validation |

### 🔧 search_snapshots & search_performance Tools

| Test Type | What to Test | Why |
|-----------|--------------|-----|
| **Unit** | Operator mapping, date filtering logic | Logic validation |
| **Integration** | STRUCT value access, numeric filtering | Schema validation |

### 🧠 Modules (intent, extraction, normalization, manager)

| Test Type | What to Test | Why |
|-----------|--------------|-----|
| **Unit** | Logic with mocked LLM calls | Fast, cheap, no API costs |
| **Integration** | Actual LLM behavior | Validate prompts work (expensive!) |

**Strategy:** Mostly unit tests with mocked LLM, few integration tests with real LLM

### 🎼 SearchManager (Orchestration)

| Test Type | What to Test | Why |
|-----------|--------------|-----|
| **Integration** | Multiple tools working together | This IS integration - no unit tests needed |

### 🎯 Complete Workflows

| Test Type | What to Test | Why |
|-----------|--------------|-----|
| **E2E** | User query → final results | Business validation |

---

## Decision Tree: Which Test Type?

```
Are you testing a single function/method?
├─ YES → Unit Test (mock dependencies)
└─ NO
   └─ Are you testing SQL queries or database interactions?
      ├─ YES → Integration Test (use db_snapshot)
      └─ NO
         └─ Are you testing multiple components together?
            ├─ YES → Integration Test (use real/realistic data)
            └─ NO
               └─ Are you testing a complete user workflow?
                  └─ YES → E2E Test
```

## Special Cases for Our Codebase

### ✅ MUST have integration tests:
1. **search_funds** - Complex SQL with STRUCT/array access
2. **search_semantic** - Vector similarity can't be mocked
3. **search_positions** - Aggregations and joins
4. **search_snapshots** - STRUCT value access
5. **search_performance** - Date filtering and joins

### ⚠️ Mostly unit tests (integration optional):
1. **intent** - Mock LLM to avoid API costs
2. **extraction** - Mock LLM to avoid API costs
3. **normalization** - Pure logic, no external deps
4. **manager** - Conversation logic can be unit tested

### ✅ Only integration tests:
1. **SearchManager** - By definition, this IS integration

### ✅ Only E2E tests:
1. **Complete user workflows** - Query to final response

---

## Cost-Benefit Analysis

### search_funds Example

**Without integration tests:**
```python
# Unit test passes ✅
def test_search_builds_query():
    assert "service_providers" in query

# Deploy to production
# User tries to search by manager
# ❌ CRASH: SQL syntax error!
# Problem: We changed service_providers structure but unit tests didn't catch it
```

**With integration tests:**
```python
# Unit test passes ✅
def test_search_builds_query():
    assert "service_providers" in query

# Integration test FAILS ❌
def test_search_with_real_schema(db_snapshot):
    results = tool.forward(...)  # SQL error caught before production!

# Fix the query
# Integration test passes ✅
# Deploy with confidence
```

**ROI:**
- Cost: ~30 seconds to run integration tests in CI
- Benefit: Catch SQL errors before production
- **Verdict: Worth it!**

---

## Best Practices

### 1. Start with Unit Tests
Write unit tests first to validate logic quickly.

### 2. Add Integration Tests for:
- Database interactions
- File I/O
- Complex data structures
- External service integration

### 3. Add E2E Tests for:
- Critical user paths
- Complex workflows
- Business requirements

### 4. Mock Expensive Operations
- LLM API calls → Mock in unit tests
- Database queries → Mock in unit tests, real in integration tests
- File I/O → Mock in unit tests when appropriate

### 5. Use Markers
```python
@pytest.mark.unit           # Fast, many
@pytest.mark.integration    # Medium, some
@pytest.mark.e2e           # Slow, few
@pytest.mark.requires_llm  # Expensive, very few
```

### 6. Run Tests at Different Stages
```bash
# During development (every save)
pytest -m unit

# Before commit (pre-commit hook)
pytest -m "unit or integration" -m "not requires_llm"

# Before deploy (CI pipeline)
pytest -m "not requires_llm"

# Nightly (full validation)
pytest  # Everything including LLM tests
```

---

## Summary

| Test Type | Count | Speed | Cost | When to Run |
|-----------|-------|-------|------|-------------|
| Unit | Many (100s) | Fast (<1s) | Free | Every save |
| Integration | Some (10s) | Medium (5s) | Cheap | Before commit |
| E2E | Few (5-10) | Slow (30s) | Medium | Before deploy |
| E2E + LLM | Very few (2-3) | Very slow (2min) | Expensive | Nightly |

**The Goal:** Maximum confidence with minimum cost.

---

## For search_funds Specifically

### We need BOTH unit and integration tests because:

1. **Unit tests** validate:
   - ✅ Query building logic is correct
   - ✅ Parameter validation works
   - ✅ Error handling is proper
   - ✅ Fast feedback during development

2. **Integration tests** validate:
   - ✅ SQL actually executes on DuckDB
   - ✅ STRUCT syntax is correct (`list_filter`, array access)
   - ✅ Schema hasn't changed
   - ✅ entity_correlations.json loads correctly
   - ✅ Service provider filtering works with real data
   - ✅ Queries perform well

### Without integration tests, we risk:
- ❌ Deploying broken SQL queries
- ❌ Schema mismatches in production
- ❌ Performance issues with real data
- ❌ STRUCT/array access errors

### With integration tests, we gain:
- ✅ Confidence that queries work on real schema
- ✅ Early detection of breaking changes
- ✅ Performance validation
- ✅ Real data validation

**Cost:** ~5 seconds in CI
**Benefit:** Prevent production incidents
**Decision:** Absolutely worth it! ✅
