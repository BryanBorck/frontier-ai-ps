# Evaluation Dataset - 260 Brazilian Fund Search Queries

This dataset contains 260 fund search queries split into:
- **103 queries** that work with CURRENT schema (ready to evaluate now)
- **157 queries** that need FUTURE features (roadmap for implementation)

---

## 📁 Folder Structure

```
evaluation/data/
├── _current_schema/         # 103 queries - CAN EVALUATE NOW ✅
│   ├── exact_match/         # 9 queries - Specific fund lookups
│   ├── single_asset_class/  # 16 queries - One investment class filter
│   ├── single_company/      # 15 queries - Company name searches
│   ├── dual_criteria/       # 21 queries - Two filters combined
│   ├── ranking_sorting/     # 19 queries - Top N funds
│   ├── browse_general/      # 8 queries - All funds
│   └── ...                  # Other categories
│
├── _future_features/        # 157 queries - NEED IMPLEMENTATION 🔮
│   ├── dual_criteria/       # 61 queries - Need sector, risk, etc.
│   ├── multi_criteria/      # 51 queries - Complex combinations
│   ├── single_fees/         # 5 queries - Need fee fields
│   ├── single_geographic/   # 5 queries - Need geographic_focus
│   └── ...                  # Other categories
│
├── README.md               # This file
└── _SPLIT_REPORT.md       # Detailed analysis
```

---

## 🎯 Current Schema (103 Queries - Ready Now)

These queries use ONLY fields that exist in the current database:

### Available Fields
- **fund_legal_name** (string) - Partial match on fund name
- **fund_type** (enum) - FI, FIP, FIDC, FII, ETF, CLASSES - FIF
- **investment_class** (enum) - Multimercado, Ações, Renda Fixa, Cambial, FIP, Dívida Externa, Imobiliário
- **fund_of_funds** (boolean) - Filter for fund-of-funds
- **target_audience** (enum) - PROFESSIONAL, QUALIFIED, RETAIL
- **manager_type** (enum) - CORPORATE, INDIVIDUAL
- **is_exclusive_fund** (boolean) - Filter for exclusive funds
- **can_invest_abroad_100_pct** (boolean) - Can invest fully abroad
- **has_long_term_taxation** (boolean) - Has long-term tax benefits

### Example Queries

```jsonl
// Exact match - Returns 1 fund
{"query": "give me bradesco gold fund", "expected_criteria": {"fund_legal_name": "Bradesco Ouro", "investment_class": "Multimercado", "fund_of_funds": true}, "expected_fund_cnpjs": ["37.235.773/0001-67"]}

// Single asset class - Returns many funds
{"query": "stocks", "expected_criteria": {"investment_class": "Ações"}}

// Dual criteria - Returns filtered list
{"query": "equity funds for retail investors", "expected_criteria": {"investment_class": "Ações", "target_audience": "RETAIL"}}

// Ranking - Returns ordered list
{"query": "top multimercado funds", "expected_criteria": {"investment_class": "Multimercado"}}
```

### Distribution
- 21 dual_criteria
- 19 ranking_sorting
- 16 single_asset_class
- 15 single_company
- 9 exact_match
- 8 browse_general
- ... and more

---

## 🔮 Future Features (157 Queries - Roadmap)

These queries need fields NOT yet implemented:

### Top Priority Fields (by demand)
1. **geographic_focus** (26 queries need it) - "latin america", "international", "brazil"
2. **strategy** (23 queries) - "growth", "value", "dividend", "aggressive"
3. **risk_profile** (18 queries) - "low risk", "conservative", "aggressive"
4. **sector** (15 queries) - "technology", "healthcare", "real estate"
5. **purpose** (12 queries) - "income", "growth", "capital preservation"
6. **esg** (11 queries) - ESG/sustainable fund filter
7. **benchmark** (10 queries) - "beats CDI", "tracks IBOVESPA"
8. **liquidity** (10 queries) - "daily liquidity", "can redeem anytime"
9. **volatility** (9 queries) - Risk metrics
10. **fees** (7 queries) - "low fee", "no performance fee"

### Example Future Queries

```jsonl
// Need sector field
{"query": "technology sector funds", "expected_criteria": {"sector": "technology", "_needs_implementation": ["sector"]}}

// Need risk_profile field
{"query": "low risk funds for retirement", "expected_criteria": {"risk_profile": "conservative", "_needs_implementation": ["risk_profile"]}}

// Need multiple future fields
{"query": "ESG technology funds with aggressive growth strategy", "expected_criteria": {"sector": "technology", "esg": true, "strategy": "aggressive_growth", "_needs_implementation": ["sector", "esg", "strategy"]}}
```

See [_SPLIT_REPORT.md](_SPLIT_REPORT.md) for full analysis.

---

## 🚀 Usage

### Load All Examples (260)
```python
from src.evaluation.fund_search_eval_dataset import FUND_SEARCH_EXAMPLES
print(f"Total: {len(FUND_SEARCH_EXAMPLES)}")  # 260
```

### Load Current Schema Only (103)
```python
from src.evaluation.fund_search_eval_dataset import load_current_schema_examples
current = load_current_schema_examples()
print(f"Can evaluate now: {len(current)}")  # 103
```

### Load Future Features (157)
```python
from src.evaluation.fund_search_eval_dataset import load_future_feature_examples
future = load_future_feature_examples()
print(f"Need implementation: {len(future)}")  # 157
```

### View Statistics
```bash
uv run python -m src.evaluation.fund_search_eval_dataset
```

---

## 📊 Evaluation Categories

Queries are organized by **expected result type** and **validation approach**:

| Category | Current | Future | Total | Validation |
|----------|---------|--------|-------|------------|
| dual_criteria | 21 | 61 | 82 | criteria_match |
| multi_criteria | 1 | 51 | 52 | criteria_match |
| ranking_sorting | 19 | 1 | 20 | ordered |
| single_asset_class | 16 | 0 | 16 | criteria_match |
| single_company | 15 | 1 | 16 | contains |
| exact_match | 9 | 6 | 15 | exact_match |
| browse_general | 8 | 0 | 8 | count_min |
| single_geographic | 2 | 5 | 7 | criteria_match |
| ... | ... | ... | ... | ... |

---

## 🧪 Validation Types

Each query specifies how to validate results:

| Type | Count | Description |
|------|-------|-------------|
| criteria_match | 50 | All results must match specified criteria |
| ordered | 19 | Results must be in correct order |
| contains | 15 | Results should contain expected items |
| exact_match | 9 | Must return exactly this fund |
| count_min | 8 | Must return minimum number of results |
| contains_all | 2 | Must include all specified items |

---

## 📝 JSONL Format

Each query is a JSON object with these fields:

```json
{
  "query": "give me bradesco gold fund",
  "expected_criteria": {
    "fund_legal_name": "Bradesco Ouro",
    "investment_class": "Multimercado",
    "fund_of_funds": true
  },
  "expected_fund_cnpjs": ["37.235.773/0001-67"],
  "description": "Direct fund lookup by branded name",
  "category": "direct_lookup",
  "eval_category": "exact_match",
  "validation_type": "exact_match"
}
```

### Key Features
- **Realistic criteria**: Uses actual fund names in Portuguese (e.g., "Bradesco Ouro" not "bradesco gold")
- **Schema-validated**: All fields exist in database schema
- **CNPJs included**: Known funds have expected CNPJs for validation
- **Future-flagged**: Queries needing new fields marked with `_needs_implementation`

---

## 🎯 Evaluation Strategy

### Phase 1: Current Schema (103 queries)
**Expected accuracy: 80%+**

1. **exact_match** (9 queries) - Should be 100% accurate
2. **single_asset_class** (16 queries) - Should be 95%+ accurate
3. **single_company** (15 queries) - Should be 90%+ accurate
4. **browse_general** (8 queries) - Should be 100% accurate

Run evaluation:
```bash
MLFLOW_ENABLED=true uv run python -m src.evaluation.evaluate
```

### Phase 2: Implement Priority Fields
Based on query demand, implement in this order:
1. geographic_focus (26 queries blocked)
2. strategy (23 queries blocked)
3. risk_profile (18 queries blocked)
4. sector (15 queries blocked)
5. purpose (12 queries blocked)

### Phase 3: Re-evaluate with New Fields
As you implement new fields, move queries from `_future_features/` to evaluation.

---

## 🛠️ Adding New Queries

### For Current Schema
Add to appropriate category in `_current_schema/`:

```bash
cd src/src/evaluation/data/_current_schema/dual_criteria
# Edit queries.jsonl, add new line:
{"query": "retail equity funds", "expected_criteria": {"investment_class": "Ações", "target_audience": "RETAIL"}, "eval_category": "dual_criteria", "validation_type": "criteria_match"}
```

### For Future Features
Add to appropriate category in `_future_features/`:

```bash
cd src/src/evaluation/data/_future_features/single_sector
# Edit queries.jsonl, add new line:
{"query": "healthcare funds", "expected_criteria": {"sector": "healthcare", "_needs_implementation": ["sector"]}, "eval_category": "single_sector", "validation_type": "criteria_match"}
```

---

## 🔍 Query Translation Examples

The dataset uses **actual Portuguese fund names and database values**:

### English → Portuguese (Investment Classes)
- "stocks" / "equity" → `"Ações"`
- "bonds" / "fixed income" → `"Renda Fixa"`
- "real estate" → `"Imobiliário"`
- "multimarket" / "hedge" → `"Multimercado"`
- "currency" / "forex" → `"Cambial"`

### Fund Names
- "bradesco gold" → `"Bradesco Ouro"` (ouro = gold)
- "santander funds" → `"santander"` (partial match)
- "itau" / "itaú" → Both work (partial match)

### Known Funds with CNPJs
- Bradesco Ouro FIF CIC Mult RL: `37.235.773/0001-67`

---

## 📈 Next Steps

1. **Run evaluation on current 103 queries**
   ```bash
   MLFLOW_ENABLED=true uv run python -m src.evaluation.evaluate
   ```

2. **Track accuracy by category** - Identify weak spots

3. **Prioritize field implementation** - Start with geographic_focus (26 queries)

4. **Add more known fund CNPJs** - Improve exact_match validation

5. **Expand current schema queries** - Add variations of working query types

---

Good luck! 🚀
