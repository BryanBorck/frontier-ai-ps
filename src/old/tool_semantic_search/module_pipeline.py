import os
from typing import Any

import duckdb
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Constants
VECTOR_DB_PATH = "src/infrastructure/database/vector_store.db"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Global model cache to avoid reloading
_MODEL_CACHE = None


def get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        print(f"Loading embedding model: {MODEL_NAME}...")
        _MODEL_CACHE = SentenceTransformer(MODEL_NAME)
    return _MODEL_CACHE


class SemanticSearchResult(BaseModel):
    legal_name: str
    cnpj: str
    investment_class: str | None = None
    score: float
    text_content: str | None = None


def search_vectors(query: str, limit: int = 5) -> list[SemanticSearchResult]:
    """
    Performs a semantic search on the fund vector database.
    Uses Multi-Query Fusion (Raw + Prefixes) to handle structured embeddings.
    """
    if not os.path.exists(VECTOR_DB_PATH):
        print(f"Warning: Vector DB not found at {VECTOR_DB_PATH}")
        return []

    model = get_model()

    # 1. Generate Query Variations
    # We embedded data with "Fund Name: ...", "Strategy Description: ...", etc.
    # The model responds better if the query matches this structure.
    queries = [
        query,  # Raw
        f"Fund Name: {query}",  # Targeted Name Search
        f"Strategy Description: {query}",  # Targeted Strategy Search
        f"Objective: {query}",  # Targeted Objective Search
    ]

    # Encode all variations
    query_vectors = model.encode(queries, convert_to_numpy=True)

    conn = duckdb.connect(VECTOR_DB_PATH, read_only=True)

    # 2. Run Searches for each variation
    # We fetch more results (limit * 20) to allow for re-ranking and fusion
    # Rank 22 was observed for correct target, so we need a wide net.
    fetch_limit = limit * 20

    all_results = {}  # Map CNPJ -> Best Score Result

    sql = """
        SELECT 
            metadata['legal_name'] as legal_name,
            cnpj,
            metadata['investment_class'] as investment_class,
            text_content,
            array_cosine_similarity(embedding, ?::FLOAT[384]) as score
        FROM fund_embeddings
        ORDER BY score DESC
        LIMIT ?
    """

    try:
        for q_vec in query_vectors:
            rows = conn.execute(sql, [q_vec, fetch_limit]).fetchall()
            for r in rows:
                # r is (legal_name, cnpj, investment_class, text_content, score)
                cnpj = r[1]
                score = float(r[4])

                # Max Pooling: Keep the highest score for this fund across all query variations
                if cnpj not in all_results or score > all_results[cnpj]["score"]:
                    all_results[cnpj] = {
                        "legal_name": r[0],
                        "cnpj": r[1],
                        "investment_class": r[2],
                        "text_content": r[3],
                        "score": score,
                    }
    except Exception as e:
        print(f"Error executing vector search: {e}")
        conn.close()
        return []

    # 3. Keyword Boost (Hybrid Search Lite)
    # If query terms appear in legal_name, boost score significantly.
    # This fixes "Bradesco Gold" finding "Gold Power" instead of "Bradesco Ouro".

    # Split query into significant terms (len > 2)
    search_terms = [w.lower() for w in query.split() if len(w) > 2]

    final_list = []
    for cnpj, data in all_results.items():
        name_lower = data["legal_name"].lower()
        boost = 0.0

        # Check for exact word matches in name
        matches = 0
        for term in search_terms:
            if term in name_lower:
                matches += 1

        # Boost Logic: +0.1 for each matched term, capped at +0.3
        # This is a heuristic to break ties or lift relevant named funds
        if matches > 0:
            boost = min(matches * 0.1, 0.3)

        data["score"] += boost
        final_list.append(data)

    conn.close()

    # 4. Sort and Limit
    final_list.sort(key=lambda x: x["score"], reverse=True)
    top_results = final_list[:limit]

    output = []
    for r in top_results:
        output.append(
            SemanticSearchResult(
                legal_name=r["legal_name"],
                cnpj=r["cnpj"],
                investment_class=r["investment_class"],
                text_content=r["text_content"][:200] + "...",
                score=r["score"],
            )
        )

    return output


def execute(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Executes the semantic search and returns a list of dictionaries.
    """
    results = search_vectors(query, limit)
    return [r.model_dump() for r in results]
