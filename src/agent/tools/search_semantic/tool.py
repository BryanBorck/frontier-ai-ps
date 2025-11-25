import dspy
import duckdb
from sentence_transformers import SentenceTransformer

from src.agent.models.fund import FundResult

# Global model cache to avoid reloading
_MODEL_CACHE = None
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = SentenceTransformer(MODEL_NAME)
    return _MODEL_CACHE


def _extract_fund_id(fund_uuid) -> str:
    """Extract clean fund_id from DuckDB's UUID format."""
    if fund_uuid is None:
        return ""

    # DuckDB returns UUIDs as dict with 'type' and 'value' keys
    if isinstance(fund_uuid, dict):
        if "value" in fund_uuid:
            return str(fund_uuid["value"])
        return str(fund_uuid)

    # Already a string
    if isinstance(fund_uuid, str):
        # Check if it's a stringified dict (sometimes happens)
        if fund_uuid.startswith("{") and "value" in fund_uuid:
            import ast
            import re

            # Try parsing with AST first
            try:
                parsed = ast.literal_eval(fund_uuid)
                if isinstance(parsed, dict) and "value" in parsed:
                    return str(parsed["value"])
            except (ValueError, SyntaxError):
                pass

            # Fallback to Regex if AST fails (e.g. unquoted symbols like INTERNAL_HASH)
            # Look for value: UUID_STRING
            # UUID pattern: 8-4-4-4-12 hex chars
            match = re.search(r"['\"]?value['\"]?\s*:\s*([0-9a-fA-F-]{36})", fund_uuid)
            if match:
                return match.group(1)

        return fund_uuid

    # Fallback
    return str(fund_uuid)


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
    ) -> list[FundResult]:
        """
        Search using multi-query fusion with keyword boosting.

        Args:
            query: Search query
            top_k: Number of results
            search_mode: "name" (prioritize name match), "strategy" (strategy/objective only), "all" (both)
            pre_filter: Optional dict of filters (e.g. {"manager": "Bradesco", "name_terms": ["Ouro"]})
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
                    fund_uuid,
                    cnpj,
                    metadata['legal_name'] as legal_name,
                    metadata['investment_class'] as investment_class,
                    text_content,
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
                        # Or simply ensuring the type appears
                        params.append(f"%Type: {pre_filter['fund_type']}%")

                    if "name_terms" in pre_filter and pre_filter["name_terms"]:
                        for term in pre_filter["name_terms"]:
                            t = f"%{term}%"
                            params.append(t)
                            params.append(t)

                params.append(fetch_limit)

                rows = conn.execute(sql, params).fetchall()
                for row in rows:
                    fund_uuid, cnpj, legal_name, investment_class, text_content, score = row

                    if score is None:
                        continue

                    fund_id = _extract_fund_id(fund_uuid)

                    if cnpj not in all_results or float(score) > all_results[cnpj]["score"]:
                        all_results[cnpj] = {
                            "fund_id": fund_id,
                            "cnpj": cnpj or "",
                            "legal_name": legal_name,
                            "investment_class": investment_class,
                            "score": float(score),
                        }

            conn.close()

            # 3. Keyword Boost (Hybrid Search)
            # Ignore generic terms to prevent boosting irrelevant funds that share these common words
            STOPWORDS = {
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

            return [
                FundResult(
                    fund_id=r["fund_id"],
                    cnpj=r["cnpj"],
                    legal_name=r["legal_name"],
                    investment_class=r["investment_class"],
                    match_score=r["score"],
                )
                for r in top_results
            ]

        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    def get_by_ids(self, fund_ids: list[str]) -> list[FundResult]:
        """Fetch funds by ID explicitly (for details/context lookup)."""
        if not fund_ids:
            return []

        try:
            conn = duckdb.connect(self.vector_store_path, read_only=True)

            # Handle potentially complex UUID formats by using ILIKE match
            likes = []
            params = []
            for fid in fund_ids:
                likes.append("CAST(fund_uuid AS VARCHAR) ILIKE ?")
                params.append(f"%{fid}%")

            where_clause = " OR ".join(likes)

            sql = f"""
                SELECT 
                    fund_uuid,
                    cnpj,
                    metadata['legal_name'] as legal_name,
                    metadata['investment_class'] as investment_class,
                    text_content
                FROM fund_embeddings
                WHERE {where_clause}
            """

            rows = conn.execute(sql, params).fetchall()

            results = []
            seen_ids = set()

            for row in rows:
                fund_uuid, cnpj, legal_name, investment_class, text_content = row
                fund_id = _extract_fund_id(fund_uuid)

                # Deduplicate and ensure match
                if fund_id not in seen_ids:
                    # Double check if this ID is actually one of requested (fuzzy match check)
                    # Since we did ILIKE, we might get false positives if ID is short?
                    # UUIDs are long enough.
                    seen_ids.add(fund_id)
                    results.append(
                        FundResult(
                            fund_id=fund_id,
                            cnpj=cnpj,
                            legal_name=legal_name,
                            investment_class=investment_class,
                            match_score=1.0,  # Exact match logic
                            description=text_content,
                        )
                    )

            conn.close()
            return results

        except Exception as e:
            print(f"Error in get_by_ids: {e}")
            return []
