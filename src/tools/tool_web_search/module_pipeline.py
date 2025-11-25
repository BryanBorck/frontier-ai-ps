"""
Exa web search tool implementation.

This module implements the core logic for searching the web using Exa AI.
"""

import os

from exa_py import Exa
from pydantic import BaseModel, Field


class ExaSearchResult(BaseModel):
    """Structured result from Exa search."""

    title: str = Field(description="Page title")
    url: str = Field(description="Page URL")
    published_date: str | None = Field(default=None, description="Publication date if available")
    author: str | None = Field(default=None, description="Author if available")
    score: float | None = Field(default=None, description="Relevance score from Exa")
    text: str | None = Field(default=None, description="Page text content (if requested)")
    highlights: list[str] | None = Field(
        default=None, description="Highlighted snippets (if requested)"
    )


def execute(
    query: str,
    num_results: int = 5,
    include_text: bool = True,
    include_highlights: bool = False,
    use_autoprompt: bool = True,
) -> list[dict]:
    """
    Execute a web search using Exa AI.

    Args:
        query: The search query to execute
        num_results: Maximum number of results to return (default: 10)
        include_text: Whether to include text content from the pages (default: True)
        include_highlights: Whether to include highlighted snippets (default: False)
        use_autoprompt: Whether to use Exa's autoprompt feature (default: True)

    Returns:
        List of search results as dictionaries

    Raises:
        ValueError: If EXA_API_KEY environment variable is not set
        Exception: If Exa API call fails
    """
    # Get API key from environment
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError(
            "EXA_API_KEY environment variable not set. Get your API key at https://exa.ai"
        )

    # Initialize Exa client
    exa = Exa(api_key=api_key)

    # Prepare search options
    search_options = {
        "num_results": num_results,
    }

    # Configure content options
    if include_text or include_highlights:
        contents = {}
        if include_text:
            contents["text"] = True
        if include_highlights:
            contents["highlights"] = True
        search_options["contents"] = contents

    # Execute search
    try:
        response = exa.search(query, **search_options)
    except Exception as e:
        raise Exception(f"Exa API search failed: {str(e)}") from e

    # Parse results
    results = []
    for result in response.results:
        search_result = ExaSearchResult(
            title=result.title or "",
            url=result.url,
            published_date=result.published_date if hasattr(result, "published_date") else None,
            author=result.author if hasattr(result, "author") else None,
            score=result.score if (hasattr(result, "score") and result.score is not None) else None,
            text=result.text if hasattr(result, "text") else None,
            highlights=result.highlights if hasattr(result, "highlights") else None,
        )
        results.append(search_result.model_dump(exclude_none=True))

    return results
