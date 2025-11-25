"""Tool: Semantic Search
Search for funds using natural language to match investment strategies, risks, and qualitative data.
"""

from .module_pipeline import execute


def tool_semantic_search(input_data: dict) -> list[dict]:
    """Main tool entry point for semantic search.

    IMPORTANT: The database contains Brazilian funds with descriptions in Portuguese.
    If the user's query is in English, YOU MUST TRANSLATE key terms to Portuguese
    for better results (e.g., search for 'Bradesco fundo ouro' instead of 'Bradesco gold fund').

    ALWAYS include the CNPJ of the found funds in your final answer to the user.

    Args:
        input_data: Dictionary with 'query' and optional 'limit'.

    Returns:
        List of dictionaries with fund metadata and relevance scores.
    """
    query = input_data.get("query")
    if not query:
        raise ValueError("Missing required field 'query'")

    limit = input_data.get("limit", 5)

    return execute(query=query, limit=limit)


class _FundSemanticSearchInternal:
    """Internal semantic search function for ReAct agent compatibility.

    This class is not part of the public tool API.
    """

    def search_semantic(self, query: str, limit: int = 5) -> list[dict]:
        """Search for funds using natural language to match investment strategies.

        IMPORTANT: The database contains Brazilian funds with descriptions in Portuguese.
        If the user's query is in English, TRANSLATE key terms to Portuguese
        (e.g., search for 'fundo ouro' instead of 'gold fund').

        ALWAYS include the CNPJ of the found funds in your final answer.

        Args:
            query: The natural language search query (e.g., 'fundo ouro').
            limit: Maximum number of results to return (default: 5).

        Returns:
            List of dictionaries with fund metadata and relevance scores.
        """
        return execute(query=query, limit=limit)


__all__ = ["tool_semantic_search", "_FundSemanticSearchInternal"]
