"""
Exa Web Search Tool

This package provides AI-powered web search capabilities using Exa AI.

Public Interface:
    tool_web_search: Main function for web search

Internal Interface:
    _WebSearchInternal: Class for ReAct agent integration
"""

from .index import _WebSearchInternal, tool_web_search
from .schema import TOOL_DESCRIPTION, TOOL_NAME, TOOL_SCHEMA

__all__ = [
    "tool_web_search",
    "_WebSearchInternal",
    "TOOL_NAME",
    "TOOL_DESCRIPTION",
    "TOOL_SCHEMA",
]
