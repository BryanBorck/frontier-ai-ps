# Tool: Semantic Search

This tool enables natural language search over the Brazilian investment fund database. It leverages vector embeddings generated from fund documentation (Fact Sheets/Lâminas) and metadata to find funds based on qualitative criteria.

## capabilities

- **Concept Matching:** Find funds based on investment themes (e.g., "crypto", "agribusiness", "gold", "tech").
- **Risk & Profile:** Search by risk tolerance (e.g., "low risk fixed income", "aggressive multimarket").
- **Manager Focus:** Find funds by specific managers if mentioned in their policies.
- **Objective Search:** Match user goals with fund objectives.

## Underlying Technology

- **Database:** `src/infrastructure/database/vector_store.db` (DuckDB)
- **Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)
- **Data Source:** CVM Lâminas (qualitative text) + CVM/Anbima Metadata (names, classes).

## Usage

**Input:**
```json
{
  "query": "fundo de investimento com exposição a ouro",
  "limit": 5
}
```

**Output:**
```json
[
  {
    "legal_name": "BRADESCO OURO FI FINANCEIRO...",
    "cnpj": "37.235.773/0001-67",
    "investment_class": "Multimercado",
    "score": 0.85,
    "text_content": "Fund Name: BRADESCO OURO... Strategy: Exposição à variação da cotação do ouro..."
  },
  ...
]
```

