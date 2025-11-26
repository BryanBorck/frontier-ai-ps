# Ambiguity Handling

## Overview

Ambiguous queries: detect → make best guess → show results → offer clarification.

## Key Flags

### `is_potentially_ambiguous` (Intent)
**Location**: [`intent.py:106`](../src/agent/fund_search/signatures/intent.py#L106)

Set when query has multiple valid interpretations.

**Examples**:
```
"bradesco gold" → Fund NAME or gold STRATEGY
"itau tech" → Fund NAME or tech STRATEGY
"Verde funds" → Manager CRITERIA or fund NAME
```

### `interpretation_note` (Intent)
**Location**: [`intent.py:114`](../src/agent/fund_search/signatures/intent.py#L114)

One-sentence explanation of chosen interpretation (only when `is_potentially_ambiguous = True`).

**Example**: `"Interpreting as Bradesco funds tracking gold prices"`

### `is_ambiguous` (Output)
**Location**: [`output.py:17`](../src/agent/fund_search/models/output.py#L17)

Set when search results need disambiguation.

**Difference**:
- `is_potentially_ambiguous`: Input has multiple meanings
- `is_ambiguous`: Output needs refinement (e.g., 50+ results)

## Response Types

| Type | When | Example |
|------|------|---------|
| `single_match` | 1 result | "Verde Scena Macro" |
| `list_results` | 2-50 results | Good match |
| `too_many_results` | 50+ results | "give me itau funds" |
| `disambiguation` | Multiple interpretations | "Did you mean X or Y?" |
| `no_results` | 0 results | No matches |
| `no_results_followup` | 0 + suggestions | "Try searching..." |

## Follow-up Fields

### `suggested_followup`
**Location**: [`output.py:20`](../src/agent/fund_search/models/output.py#L20)

Natural language prompt for refinement.

**Example**: `"Are you looking for a specific asset class or fund type?"`

### `suggestions`
**Location**: [`output.py:21`](../src/agent/fund_search/models/output.py#L21)

List of specific refinement options.

**Example**:
```python
suggestions = [
    "Buscar por Classe de Ativo",
    "Buscar por Tipo de Fundo",
    "Fundos de Alto Retorno"
]
```

## Flow

```
Query → Intent (is_potentially_ambiguous, interpretation_note)
      → Extraction (uses chosen interpretation)
      → Search (returns CNPJs)
      → Manager (sets is_ambiguous, suggested_followup, suggestions)
      → Response (includes interpretation_note + followups)
```

## Example

```
User: "bradesco gold"

Intent:
  is_potentially_ambiguous: True
  interpretation_note: "Interpreting as Bradesco gold tracking funds"
  intents: ["find_by_strategy"]

Search:
  → 3 funds found
  response_type: "list_results"

Response:
  "Here are Bradesco funds that invest in gold:
   1. Bradesco Ouro FIA
   2. Bradesco Commodities

   I interpreted this as Bradesco funds tracking gold prices.

   Did you mean a specific fund name instead?"
```

## Implementation Files

- Intent: [`signatures/intent.py`](../src/agent/fund_search/signatures/intent.py)
- Output: [`models/output.py`](../src/agent/fund_search/models/output.py)
- Manager: [`modules/manager.py`](../src/agent/fund_search/modules/manager.py)
- Orchestrator: [`orchestrator.py`](../src/agent/fund_search/orchestrator.py)
