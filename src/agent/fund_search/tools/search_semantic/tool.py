import dspy
import duckdb
from sentence_transformers import SentenceTransformer

from src.agent.fund_search.models.fund import FundResult

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
            # Clean query: remove quotes and extra whitespace
            clean_query = query.replace('"', "").replace("'", "").strip()

            model = _get_model()
            conn = duckdb.connect(self.vector_store_path, read_only=True)

            # 1. Generate Query Variations based on search_mode
            if search_mode == "name":
                queries = [clean_query, f"Fund Name: {clean_query}"]
            elif search_mode == "strategy":
                queries = [
                    f"Strategy Description: {clean_query}",
                    f"Objective: {clean_query}",
                ]
            else:
                queries = [
                    clean_query,
                    f"Fund Name: {clean_query}",
                    f"Strategy Description: {clean_query}",
                    f"Objective: {clean_query}",
                ]

            # Encode all variations
            query_vectors = model.encode(queries, convert_to_numpy=True)

            # 2. Run searches using DuckDB's native cosine similarity
            fetch_limit = top_k * 20
            all_results: dict[str, dict] = {}

            # Construct SQL with filters
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
                    # We search for the type in text content
                    where_clauses.append("text_content ILIKE ?")

                if "name_terms" in pre_filter and pre_filter["name_terms"]:
                    for _ in pre_filter["name_terms"]:
                        # Filter by required terms in legal_name or text_content
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

            # 3. Keyword Boost (Hybrid Search)
            STOPWORDS = {
                "fundo", "investimento", "investimentos", "cotas", "classe", "fi", "fif", "fic",
                "fim", "fia", "multimercado", "renda", "fixa", "acoes", "cambial",
                "referenciado", "credito", "privado", "financeiro", "banco", "asset", "gestao",
            }

            search_terms = [
                w.lower() for w in clean_query.split() if len(w) > 2 and w.lower() not in STOPWORDS
            ]

            final_list = []
            for _cnpj, data in all_results.items():
                name_lower = (data["legal_name"] or "").lower()
                matches = sum(1 for term in search_terms if term in name_lower)
                if matches > 0:
                    data["score"] += min(matches * 0.1, 0.3)
                final_list.append(data)

            # 4. Sort and limit
            final_list.sort(key=lambda x: x["score"], reverse=True)
            top_results = final_list[:top_k]

            return [r["cnpj"] for r in top_results if r["cnpj"]]

        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    def get_by_ids(self, fund_ids: list[str]) -> list[FundResult]:
        """
        Deprecated or Refactored? 
        The semantic tool shouldn't really be used for ID lookup if we have the details tool.
        But maybe we still need it for resolving text content?
        
        The user wants separate detail tool. 
        I'll leave this here for now but it might not be used.
        """
        # ... implementation omitted/kept as is if needed, but the new architecture relies on CNPJs ...
        # If the user iterates on CNPJs, we don't need get_by_ids (which was UUID based).
        # I'll modify it to get_by_cnpjs if needed, or remove.
        return []
