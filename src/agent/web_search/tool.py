import os
import dspy
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

class WebSearchTool(dspy.Module):
    """
    Tool for searching the web using Exa AI.
    """
    def __init__(self):
        super().__init__()
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            raise ValueError(
                "EXA_API_KEY environment variable not set. Get your API key at https://exa.ai"
            )
        self.exa = Exa(api_key=api_key)

    def forward(
        self,
        query: str,
        num_results: int = 5,
        include_text: bool = True,
        include_highlights: bool = False,
    ) -> list[dict]:
        """
        Execute a web search using Exa AI.
        """
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

        try:
            response = self.exa.search(query, **search_options)
        except Exception as e:
            print(f"Exa API search failed: {str(e)}")
            return []

        # Parse results
        results = []
        for result in response.results:
            search_result = ExaSearchResult(
                title=result.title or "",
                url=result.url,
                published_date=getattr(result, "published_date", None),
                author=getattr(result, "author", None),
                score=getattr(result, "score", None),
                text=getattr(result, "text", None),
                highlights=getattr(result, "highlights", None),
            )
            results.append(search_result.model_dump(exclude_none=True))

        return results

