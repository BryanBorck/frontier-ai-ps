# Intents & Tool Strategy

## Core Design Philosophy

We moved away from a generic "chat with data" model to a **deterministic, intent-driven architecture**. The agent first explicitly classifies _what_ the user wants (the Intent) before deciding _how_ to get it (the Tool). This prevents the "Jack of all trades, master of none" problem common in LLM agents.

## Intent Classification

Instead of a single `search` intent, we now have granular intents that map directly to specific search strategies. This allows us to handle nuance:

| Intent                   | Purpose                                  | Example                                         | Search Strategy                                                                                        |
| ------------------------ | ---------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **`find_by_name`**       | User knows the fund/manager name.        | "Verde Scena", "Alaska Black"                   | **Fuzzy Match**: Focuses on exact or near-exact string matches in the `funds` table.                   |
| **`find_by_strategy`**   | User describes a theme, sector, or goal. | "Tech funds", "Bradesco Gold", "ESG"            | **Semantic Search**: Uses vector embeddings to match the _meaning_ against fund Lâminas (fact sheets). |
| **`find_by_criteria`**   | User specifies strict metadata filters.  | "FIP funds", "Qualified investors only"         | **Structured SQL**: Maps directly to `fund_type`, `audience`, or `class` columns in DuckDB.            |
| **`find_by_exposure`**   | User asks about asset holdings.          | "Funds holding Petrobras", "Exposure to crypto" | **Position Search**: Joins `funds` with `positions` to find indirect exposure.                         |
| **`has_numeric_filter`** | User applies strict math limits.         | "Returns > 10%", "Vol < 5%", "Top 10"           | **Performance SQL**: Filters on `fund_performance_indicators` or `fund_snapshots`.                     |
| **`general_browse`**     | Pagination or broad exploration.         | "Show me more", "What else?"                    | **Context Pagination**: Retrieves next page from previous result set.                                  |

### Handling Ambiguity

Users are often vague. The system handles this via:

1.  **Ambiguity Detection:** The classifier flags if a query like "Bradesco Gold" could mean "Fund named Bradesco Gold" OR "Bradesco fund investing in Gold".
2.  **Interpretation Notes:** The agent returns a note explaining its choice (e.g., "Interpreted as strategy 'Gold', not name").
3.  **Context Status:** Determines if we should `reset` filters, `keep` refining, or `refine_result_set` (filter within current results).

## Tool Selection

We avoid generic code execution. Each intent routes to a specialized tool:

- **Quantitative Tools (SQL/DuckDB):** Used for `find_by_criteria`, `has_numeric_filter`, `find_by_exposure`. Guarantees mathematical accuracy.
- **Qualitative Tools (Vector Store):** Used for `find_by_strategy`. Captures semantic meaning that SQL cannot.
- **Hybrid Approach:** A query like "Tech funds with >10% return" triggers _both_:
  1.  Vector search finds "Tech" funds.
  2.  SQL filters those results by "Return > 10%".
