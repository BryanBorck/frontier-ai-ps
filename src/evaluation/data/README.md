# Fund Search Evaluation Data

This directory contains the evaluation datasets for the Fund Search Agent.

## Current Datasets

### `fund_search_evaluation_300.jsonl`
The primary dataset containing 300 curated queries across various categories and difficulty tiers.

**Schema:**
```json
{
  "id": 1,
  "query": "FIP funds",
  "expected_intents": ["find_by_criteria"],
  "expected_extraction": {"fund_type": ["FIP"]},
  "expected_response_type": "list_results",
  "evaluation_type": "extraction_match",
  "why_tricky": "Direct fund type filter",
  "tier": 1,
  "category": "fund_type",
  "ground_truth_cnpjs": ["..."],
  "ground_truth_note": "...",
  "must_include_any": true,
  "min_results": 3
}
```

**Tiers:**
1. **Basic**: Simple criteria, single filters.
2. **Intermediate**: Dual criteria, numeric filters, simple themes.
3. **Advanced**: Ambiguous queries, manager vs strategy conflicts, complex semantic searches.
4. **Edge Cases**: Vague queries, typos, conversational/contextual queries.

### `fund_search_evaluation_summary.md`
A breakdown of the dataset composition.

## Usage

These files are loaded by `src/evaluation/core/dataset.py` for use in optimization (DSPy) and evaluation (MLflow).
