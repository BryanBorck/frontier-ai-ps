# Dataset Split Report

## Overview
- **Total queries**: 260
- **Current schema (can evaluate now)**: 103
- **Future features (need implementation)**: 157

## Distribution by Category

### Current Schema Queries (103 total)

- **dual_criteria**: 21 queries
- **ranking_sorting**: 19 queries
- **single_asset_class**: 16 queries
- **single_company**: 15 queries
- **exact_match**: 9 queries
- **single_other**: 9 queries
- **browse_general**: 8 queries
- **comparison**: 2 queries
- **single_geographic**: 2 queries
- **multi_criteria**: 1 queries
- **single_accessibility**: 1 queries

### Future Feature Queries (157 total)

- **dual_criteria**: 61 queries
- **multi_criteria**: 51 queries
- **single_accessibility**: 7 queries
- **exact_match**: 6 queries
- **single_fees**: 5 queries
- **single_geographic**: 5 queries
- **single_liquidity**: 5 queries
- **single_purpose**: 4 queries
- **single_esg**: 3 queries
- **single_tax**: 3 queries
- **single_risk**: 2 queries
- **single_sector**: 2 queries
- **ranking_sorting**: 1 queries
- **single_company**: 1 queries
- **single_strategy**: 1 queries

## Most Needed Future Fields

- **geographic_focus**: 26 queries need this
- **strategy**: 23 queries need this
- **risk_profile**: 18 queries need this
- **sector**: 15 queries need this
- **purpose**: 12 queries need this
- **esg**: 11 queries need this
- **benchmark**: 10 queries need this
- **liquidity**: 10 queries need this
- **volatility**: 9 queries need this
- **fee_level**: 7 queries need this
- **distribution_frequency**: 7 queries need this
- **max_minimum_investment**: 7 queries need this
- **pension_fund**: 6 queries need this
- **suitability**: 6 queries need this
- **time_horizon**: 5 queries need this
- **commodity**: 4 queries need this
- **uses_leverage**: 4 queries need this
- **objective**: 4 queries need this
- **currency**: 3 queries need this
- **performance_fee**: 3 queries need this


## Usage

### Evaluate Current Schema
```bash
# Only load queries from _current_schema folder
uv run python -m evaluation.evaluate
```

### View Future Features Roadmap
```bash
# Review queries in _future_features folder to prioritize implementation
cat src/evaluation/data/_future_features/*/queries.jsonl | grep '_needs_implementation'
```

## Priority Implementation Order

Based on query count, implement these fields first:
1. **geographic_focus** - 26 queries
2. **strategy** - 23 queries
3. **risk_profile** - 18 queries
4. **sector** - 15 queries
5. **purpose** - 12 queries
6. **esg** - 11 queries
7. **benchmark** - 10 queries
8. **liquidity** - 10 queries
9. **volatility** - 9 queries
10. **fee_level** - 7 queries
