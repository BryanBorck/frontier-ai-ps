"""
Integration tests for the Exa web search tool.

These tests verify end-to-end functionality with the real Exa API.
Requires EXA_API_KEY environment variable to be set.
"""

import os

import pytest

from src.tools.tool_web_search.index import _WebSearchInternal, tool_web_search


@pytest.mark.skipif(
    not os.getenv("EXA_API_KEY"), reason="EXA_API_KEY not set - skipping integration tests"
)
class TestWebSearchIntegration:
    """Integration tests with real Exa API."""

    def test_search_technical_content(self):
        """Test searching for technical content."""
        result = tool_web_search(
            {
                "query": "Python asyncio best practices",
                "num_results": 5,
                "include_text": True,
                "use_autoprompt": True,
            }
        )

        assert isinstance(result, list)
        assert len(result) > 0, "Should return at least one result"
        assert len(result) <= 5, "Should not exceed requested limit"

        # Verify result structure
        first_result = result[0]
        assert "title" in first_result
        assert "url" in first_result
        assert "score" in first_result
        assert isinstance(first_result["score"], (int, float))
        assert first_result["score"] > 0

        # Verify URL format
        assert first_result["url"].startswith("http")

        # Verify text content if included
        if "text" in first_result:
            assert isinstance(first_result["text"], str)
            assert len(first_result["text"]) > 0

    def test_search_with_highlights(self):
        """Test searching with highlight snippets."""
        result = tool_web_search(
            {
                "query": "machine learning transformers architecture",
                "num_results": 3,
                "include_text": False,
                "include_highlights": True,
            }
        )

        assert isinstance(result, list)
        if result and "highlights" in result[0]:
            assert isinstance(result[0]["highlights"], list)

    def test_search_recent_news(self):
        """Test searching for recent content."""
        result = tool_web_search(
            {
                "query": "latest developments in artificial intelligence",
                "num_results": 5,
                "include_text": False,
                "use_autoprompt": True,
            }
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Check if any results have publication dates
        for r in result:
            if "published_date" in r:
                assert isinstance(r["published_date"], str)

    def test_search_with_minimal_text(self):
        """Test search without text content for faster responses."""
        result = tool_web_search(
            {
                "query": "quantum computing",
                "num_results": 3,
                "include_text": False,
            }
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Verify no text content is included
        for r in result:
            # Text should either not be present or be None
            assert r.get("text") is None or "text" not in r

    def test_internal_class_integration(self):
        """Test the internal class used for ReAct agents."""
        searcher = _WebSearchInternal()
        result = searcher.search(
            query="data science tools",
            num_results=3,
            include_text=False,
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) <= 3

        for r in result:
            assert "title" in r
            assert "url" in r
            assert "score" in r

    def test_various_query_types(self):
        """Test different types of queries."""
        queries = [
            "explain neural networks",  # Explanation query
            "best React frameworks 2024",  # List query
            "how to optimize database queries",  # How-to query
            "artificial intelligence research papers",  # Research query
        ]

        for query in queries:
            result = tool_web_search(
                {
                    "query": query,
                    "num_results": 2,
                    "include_text": False,
                }
            )

            assert isinstance(result, list), f"Failed for query: {query}"
            assert len(result) > 0, f"No results for query: {query}"

    def test_autoprompt_comparison(self):
        """Test search with and without autoprompt."""
        query = "Python web frameworks"

        # With autoprompt
        result_with = tool_web_search(
            {
                "query": query,
                "num_results": 3,
                "use_autoprompt": True,
                "include_text": False,
            }
        )

        # Without autoprompt
        result_without = tool_web_search(
            {
                "query": query,
                "num_results": 3,
                "use_autoprompt": False,
                "include_text": False,
            }
        )

        # Both should return results
        assert len(result_with) > 0
        assert len(result_without) > 0

        # Results might differ, but both should be valid
        for result_set in [result_with, result_without]:
            for r in result_set:
                assert "title" in r
                assert "url" in r
                assert "score" in r

    def test_result_scores(self):
        """Test that results are ordered by relevance score."""
        result = tool_web_search(
            {
                "query": "deep learning frameworks",
                "num_results": 5,
                "include_text": False,
            }
        )

        assert len(result) > 1, "Need multiple results to test ordering"

        # Extract scores
        scores = [r["score"] for r in result]

        # Scores should be in descending order (highest relevance first)
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], f"Results not ordered by score: {scores}"

    def test_url_accessibility(self):
        """Test that returned URLs are valid and accessible."""
        result = tool_web_search(
            {
                "query": "software engineering best practices",
                "num_results": 3,
                "include_text": False,
            }
        )

        assert len(result) > 0

        for r in result:
            url = r["url"]
            # Basic URL validation
            assert url.startswith("http://") or url.startswith("https://")
            assert "." in url  # Should have a domain
            assert " " not in url  # No spaces in URLs
