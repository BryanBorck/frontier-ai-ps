"""
Unit tests for the Exa web search tool.

These tests verify the tool's interface and basic functionality.
"""

import os

import pytest

from src.tools.tool_web_search.index import _WebSearchInternal, tool_web_search
from src.tools.tool_web_search.module_pipeline import execute


class TestPublicInterface:
    """Test the public tool_web_search(input_data) interface."""

    def test_missing_query_raises_error(self):
        """Test that missing query parameter raises ValueError."""
        with pytest.raises(ValueError, match="Missing required field 'query'"):
            tool_web_search({})

    def test_empty_query_raises_error(self):
        """Test that empty query parameter raises ValueError."""
        with pytest.raises(ValueError, match="Missing required field 'query'"):
            tool_web_search({"query": ""})

    @pytest.mark.skipif(not os.getenv("EXA_API_KEY"), reason="EXA_API_KEY not set")
    def test_valid_query_returns_results(self):
        """Test that a valid query returns search results."""
        result = tool_web_search(
            {
                "query": "Python programming language",
                "num_results": 3,
                "include_text": False,
            }
        )

        # Verify result structure
        assert isinstance(result, list)
        assert len(result) <= 3
        if result:
            first_result = result[0]
            assert "title" in first_result
            assert "url" in first_result
            assert "score" in first_result
            assert isinstance(first_result["url"], str)
            assert first_result["url"].startswith("http")

    @pytest.mark.skipif(not os.getenv("EXA_API_KEY"), reason="EXA_API_KEY not set")
    def test_default_parameters(self):
        """Test that default parameters are applied correctly."""
        result = tool_web_search({"query": "test query"})

        assert isinstance(result, list)
        # Default is 10 results, but API might return fewer
        assert len(result) <= 10

    @pytest.mark.skipif(not os.getenv("EXA_API_KEY"), reason="EXA_API_KEY not set")
    def test_include_text_parameter(self):
        """Test that include_text parameter works."""
        result = tool_web_search(
            {
                "query": "AI research",
                "num_results": 2,
                "include_text": True,
            }
        )

        if result:
            # At least one result should have text content
            has_text = any("text" in r for r in result)
            assert has_text, "Expected at least one result with text content"


class TestInternalInterface:
    """Test the _WebSearchInternal class (for ReAct agent compatibility)."""

    def test_internal_class_instantiation(self):
        """Test that internal class can be instantiated."""
        searcher = _WebSearchInternal()
        assert hasattr(searcher, "search")
        assert callable(searcher.search)

    @pytest.mark.skipif(not os.getenv("EXA_API_KEY"), reason="EXA_API_KEY not set")
    def test_internal_search_method(self):
        """Test the search method of internal class."""
        searcher = _WebSearchInternal()
        result = searcher.search(query="machine learning", num_results=2, include_text=False)

        assert isinstance(result, list)
        assert len(result) <= 2
        if result:
            assert "title" in result[0]
            assert "url" in result[0]


class TestModulePipeline:
    """Test the execute function in module_pipeline."""

    def test_missing_api_key_raises_error(self, monkeypatch):
        """Test that missing API key raises ValueError."""
        monkeypatch.delenv("EXA_API_KEY", raising=False)

        with pytest.raises(ValueError, match="EXA_API_KEY environment variable not set"):
            execute(query="test")

    @pytest.mark.skipif(not os.getenv("EXA_API_KEY"), reason="EXA_API_KEY not set")
    def test_execute_with_minimal_params(self):
        """Test execute function with minimal parameters."""
        result = execute(query="Python", num_results=1)

        assert isinstance(result, list)
        if result:
            assert "title" in result[0]
            assert "url" in result[0]
            assert "score" in result[0]

    @pytest.mark.skipif(not os.getenv("EXA_API_KEY"), reason="EXA_API_KEY not set")
    def test_execute_with_all_params(self):
        """Test execute function with all parameters."""
        result = execute(
            query="artificial intelligence",
            num_results=3,
            include_text=True,
            include_highlights=True,
            use_autoprompt=True,
        )

        assert isinstance(result, list)
        assert len(result) <= 3


class TestSchema:
    """Test schema definitions."""

    def test_schema_exists(self):
        """Test that schema is properly loaded."""
        from src.tools.tool_web_search.schema import (
            INPUT_SCHEMA,
            OUTPUT_SCHEMA,
            TOOL_DESCRIPTION,
            TOOL_NAME,
            TOOL_SCHEMA,
        )

        assert TOOL_NAME == "tool_web_search"
        assert isinstance(TOOL_DESCRIPTION, str)
        assert isinstance(INPUT_SCHEMA, dict)
        assert isinstance(OUTPUT_SCHEMA, dict)
        assert isinstance(TOOL_SCHEMA, dict)

    def test_input_schema_structure(self):
        """Test input schema has required fields."""
        from src.tools.tool_web_search.schema import INPUT_SCHEMA

        assert "query" in INPUT_SCHEMA
        assert INPUT_SCHEMA["query"]["type"] == "string"
        assert "num_results" in INPUT_SCHEMA
        assert "include_text" in INPUT_SCHEMA
        assert "use_autoprompt" in INPUT_SCHEMA

    def test_output_schema_structure(self):
        """Test output schema structure."""
        from src.tools.tool_web_search.schema import OUTPUT_SCHEMA

        assert OUTPUT_SCHEMA["type"] == "array"
        assert "items" in OUTPUT_SCHEMA
        items = OUTPUT_SCHEMA["items"]
        assert "properties" in items
        assert "title" in items["properties"]
        assert "url" in items["properties"]
        assert "score" in items["properties"]
