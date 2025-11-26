import dspy
import duckdb
from sentence_transformers import SentenceTransformer

# Global model cache to avoid reloading
_MODEL_CACHE = None
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = SentenceTransformer(MODEL_NAME)
    return _MODEL_CACHE


class SemanticSearchTool(dspy.Module):
    """
    Semantic search tool using multi-query fusion and keyword boosting.
    Uses DuckDB's native vector similarity for performance.
    """

    def __init__(self, vector_store_path: str):
        super().__init__()
        self.vector_store_path = vector_store_path

    def forward(
        self,
        query: str,
        top_k: int = 20,
        search_mode: str = "all",
        pre_filter: dict | None = None,
    ) -> list[str]:
        """
        Search using multi-query fusion with keyword boosting.
        Returns list of CNPJs sorted by relevance.
        """
        try:
            # Clean query: remove quotes and extra whitespace (prevents SQL injection)
            clean_query = query.replace('"', "").replace("'", "").strip()

            model = _get_model()
            conn = duckdb.connect(self.vector_store_path, read_only=True)

            # 1. MULTI-QUERY FUSION: Generate multiple query variations to improve recall
            # WHY: Different query formulations match different parts of fund descriptions
            # e.g., "small cap" matches better when prefixed with "Strategy Description:"
            if search_mode == "name":
                # Focus on fund names only
                queries = [clean_query, f"Fund Name: {clean_query}"]
            elif search_mode == "strategy":
                # Focus on investment strategy/objective text
                queries = [
                    f"Strategy Description: {clean_query}",
                    f"Objective: {clean_query}",
                ]
            else:
                # Comprehensive search across all fields
                queries = [
                    clean_query,
                    f"Fund Name: {clean_query}",
                    f"Strategy Description: {clean_query}",
                    f"Objective: {clean_query}",
                ]

            # Encode all variations into embeddings
            query_vectors = model.encode(queries, convert_to_numpy=True)

            # 2. VECTOR SEARCH: Run searches using DuckDB's native cosine similarity
            # WHY: Each query variation retrieves top matches, then we take the max score per fund
            fetch_limit = top_k * 20  # Over-fetch to ensure diversity after deduplication
            all_results: dict[str, dict] = {}

            # 3. PRE-FILTERING: Apply SQL filters BEFORE vector search for efficiency
            # WHY: Reduces search space and improves performance by filtering at database level
            # Example: Filter to only "Renda Fixa" funds before computing semantic similarity
            where_clauses = []
            if pre_filter:
                if "manager" in pre_filter and pre_filter["manager"]:
                    # Filter by manager in text_content or legal_name (case insensitive)
                    where_clauses.append("(text_content ILIKE ? OR metadata['legal_name'] ILIKE ?)")

                if "investment_class" in pre_filter and pre_filter["investment_class"]:
                    # Exact/Like match on investment_class metadata
                    where_clauses.append("metadata['investment_class'] ILIKE ?")

                if "fund_type" in pre_filter and pre_filter["fund_type"]:
                    # Filter text_content for "Type: ... <type>"
                    where_clauses.append("text_content ILIKE ?")

                if "name_terms" in pre_filter and pre_filter["name_terms"]:
                    # Filter by required terms in legal_name or text_content (AND logic)
                    for _ in pre_filter["name_terms"]:
                        where_clauses.append(
                            "(metadata['legal_name'] ILIKE ? OR text_content ILIKE ?)"
                        )

            where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            sql = f"""
                SELECT 
                    cnpj,
                    metadata['legal_name'] as legal_name,
                    array_cosine_similarity(embedding, ?::FLOAT[384]) as score
                FROM fund_embeddings
                {where_sql}
                ORDER BY score DESC
                LIMIT ?
            """

            for q_vec in query_vectors:
                params = [q_vec.tolist()]

                # Add filter params (order must match where_clauses append order)
                if pre_filter:
                    if "manager" in pre_filter and pre_filter["manager"]:
                        mgr = pre_filter["manager"]
                        params.append(f"%{mgr}%")
                        params.append(f"%{mgr}%")

                    if "investment_class" in pre_filter and pre_filter["investment_class"]:
                        # Use wildcard for robustness if class name varies slightly
                        params.append(f"%{pre_filter['investment_class']}%")

                    if "fund_type" in pre_filter and pre_filter["fund_type"]:
                        # Match "Type: ... <fund_type>" pattern loosely
                        params.append(f"%Type: {pre_filter['fund_type']}%")

                    if "name_terms" in pre_filter and pre_filter["name_terms"]:
                        for term in pre_filter["name_terms"]:
                            t = f"%{term}%"
                            params.append(t)
                            params.append(t)

                params.append(fetch_limit)

                rows = conn.execute(sql, params).fetchall()
                for row in rows:
                    cnpj, legal_name, score = row

                    if score is None:
                        continue

                    if cnpj not in all_results or float(score) > all_results[cnpj]["score"]:
                        all_results[cnpj] = {
                            "cnpj": cnpj or "",
                            "legal_name": legal_name,
                            "score": float(score),
                        }

            conn.close()

            # 4. KEYWORD BOOSTING: Hybrid search combining semantic + exact matches
            # WHY: Improves precision when user mentions specific fund names or brands
            # Example: Query "XP" should rank XP-branded funds higher even if semantic match is weaker
            STOPWORDS = {
                # Common Portuguese fund terms that don't add specificity
                "fundo",
                "investimento",
                "investimentos",
                "cotas",
                "classe",
                "fi",
                "fif",
                "fic",
                "fim",
                "fia",
                "multimercado",
                "renda",
                "fixa",
                "acoes",
                "cambial",
                "referenciado",
                "credito",
                "privado",
                "financeiro",
                "banco",
                "asset",
                "gestao",
            }

            # Extract meaningful keywords from query (remove stopwords)
            search_terms = [
                w.lower() for w in clean_query.split() if len(w) > 2 and w.lower() not in STOPWORDS
            ]

            # Apply keyword boost: +0.1 per keyword match (max +0.3)
            # WHY: Balances semantic similarity with exact keyword matches
            final_list = []
            for _cnpj, data in all_results.items():
                name_lower = (data["legal_name"] or "").lower()
                matches = sum(1 for term in search_terms if term in name_lower)
                if matches > 0:
                    # Boost score by 0.1 per match, capped at 0.3 to avoid overpowering semantic score
                    data["score"] += min(matches * 0.1, 0.3)
                final_list.append(data)

            # 5. RANKING: Sort by final score and return top K
            final_list.sort(key=lambda x: x["score"], reverse=True)
            top_results = final_list[:top_k]

            return [r["cnpj"] for r in top_results if r["cnpj"]]

        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
