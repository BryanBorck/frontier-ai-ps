# Data Pipeline & Hybrid Search

## The Hybrid Challenge
Financial search requires two opposing capabilities:
1.  **Exactness:** "Funds with > 15% return" must be mathematically precise.
2.  **Semantics:** "Funds that hedge against inflation" is a linguistic concept, not a database column.

## 1. Quantitative Engine (DuckDB)
**Source:** CVM Open Data (Daily snapshots, Balancetes).
**File:** `src/infrastructure/database/br_funds.db`

Used for:
- **Performance:** Calculation of returns (12m, YTD), Volatility, Sharpe.
- **Holdings:** Deep search into `positions` table (2.5M+ rows) to find specific asset exposure.
- **Metadata:** Filtering by CNPJ, Manager Name, Condominium Type.

## 2. Qualitative Engine (Vector Store)
**Source:** CVM Lâminas (Fact Sheets), Regulations, and textual descriptions.
**Embedding Model:** `text-embedding-3-small` (or similar).

### The "Qualitative Gap"
We introduced this layer because **Structured Data is not enough.**
- **The Problem:** A database column can tell you a fund is "Multimercado", but it cannot tell you *how* it invests. Is it a "Macro" fund? Does it use "Long & Short" strategies? Does it hedge with "Crypto"?
- **The Solution:** We ingest the PDF "Lâminas" (Fact Sheets) where managers describe their strategy in plain text.
- **Semantic Matching:** By embedding these descriptions, we can match abstract user goals ("low volatility for retirement") to concrete fund strategies described in the documents.

## 3. The Search Manager
The `SearchManager` acts as the broker between these two worlds.
- **Intersection:** When a query has both types of criteria, we perform an intersection of CNPJs.
- **Ranking:** Results are ranked. Exact matches (Name/CNPJ) take precedence over Semantic matches, which take precedence over broad Criteria matches.
