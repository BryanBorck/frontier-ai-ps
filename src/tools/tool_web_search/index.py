"""
Exa Web Search Tool

This tool enables AI-powered web search using Exa AI, providing high-quality,
semantically relevant search results with optional content extraction.

Public Interface:
    tool_web_search(input_data: dict) -> list[dict]
        Main entry point for the tool, accepts a dictionary with search parameters

Internal Interface (for ReAct Agent):
    _ExaSearchInternal
        Internal class with methods that can be registered as agent tools
"""

from .module_pipeline import execute


def tool_web_search(input_data: dict) -> list[dict]:
    """
    Search the web using Exa AI.

    This is the public interface for the Exa search tool. It accepts a dictionary
    of parameters and returns a list of search results.

    Args:
        input_data: Dictionary with the following keys:
            - query (str, required): The search query to execute
            - num_results (int, optional): Maximum number of results (default: 10)
            - include_text (bool, optional): Include page content (default: True)
            - include_highlights (bool, optional): Include snippets (default: False)
            - use_autoprompt (bool, optional): Use Exa autoprompt (default: True)

    Returns:
        List of dictionaries containing search results with:
            - title: Page title
            - url: Page URL
            - score: Relevance score
            - published_date: Publication date (if available)
            - author: Author (if available)
            - text: Page content (if include_text=True)
            - highlights: Highlighted snippets (if include_highlights=True)

    Raises:
        ValueError: If required field 'query' is missing or EXA_API_KEY not set
        Exception: If Exa API call fails

    Example:
        >>> results = tool_web_search(
        ...     {"query": "latest AI research papers", "num_results": 5, "include_text": True}
        ... )
        >>> print(results[0]["title"])
        'Attention Is All You Need'
    """
    # Validate required fields
    query = input_data.get("query")
    if not query:
        raise ValueError("Missing required field 'query'")

    # Extract optional parameters with defaults
    num_results = input_data.get("num_results", 10)
    include_text = input_data.get("include_text", True)
    include_highlights = input_data.get("include_highlights", False)
    use_autoprompt = input_data.get("use_autoprompt", True)

    # Delegate to module pipeline
    return execute(
        query=query,
        num_results=num_results,
        include_text=include_text,
        include_highlights=include_highlights,
        use_autoprompt=use_autoprompt,
    )


class _WebSearchInternal:
    """
    Internal class for ReAct agent compatibility.

    This class provides methods that can be registered as tools for the dspy.ReAct
    framework. The methods wrap the execute() function with agent-friendly signatures.

    Usage:
        >>> from src.tools.tool_web_search.index import _WebSearchInternal
        >>> searcher = _WebSearchInternal()
        >>> agent = dspy.ReAct(signature="question -> answer", tools=[searcher.search], max_iters=5)
    """

    def web_search(
        self,
        query: str,
        num_results: int = 10,
        include_text: bool = True,
        include_highlights: bool = False,
        use_autoprompt: bool = True,
    ) -> list[dict]:
        """
        Search the web using Exa AI (agent-compatible method).

        Args:
            query: The search query to execute
            num_results: Maximum number of results to return (default: 10)
            include_text: Whether to include page content (default: True)
            include_highlights: Whether to include snippets (default: False)
            use_autoprompt: Whether to use Exa's autoprompt (default: True)

        Returns:
            List of search results as dictionaries

        Raises:
            ValueError: If EXA_API_KEY is not set
            Exception: If Exa API call fails
        """
        return execute(
            query=query,
            num_results=num_results,
            include_text=include_text,
            include_highlights=include_highlights,
            use_autoprompt=use_autoprompt,
        )


# Public exports
__all__ = ["tool_web_search", "_WebSearchInternal"]
