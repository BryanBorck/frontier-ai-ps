"""
Example usage of the Exa web search tool.

This script demonstrates different ways to use the tool_web_search function.
"""

import os
from pprint import pprint

from src.tools.tool_web_search import tool_web_search


def example_basic_search():
    """Example 1: Basic web search."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Web Search")
    print("=" * 60)

    results = tool_web_search(
        {
            "query": "latest developments in large language models",
            "num_results": 3,
            "include_text": False,  # Faster, metadata only
        }
    )

    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Score: {result['score']:.4f}")
        if result.get("published_date"):
            print(f"   Published: {result['published_date']}")
        print()


def example_search_with_content():
    """Example 2: Search with full text content."""
    print("\n" + "=" * 60)
    print("Example 2: Search with Content Extraction")
    print("=" * 60)

    results = tool_web_search(
        {
            "query": "Python async/await tutorial",
            "num_results": 2,
            "include_text": True,
            "use_autoprompt": True,
        }
    )

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   {result['url']}")
        if result.get("text"):
            # Show first 300 characters of content
            preview = result["text"][:300].replace("\n", " ")
            print(f"   Content: {preview}...")
        print()


def example_search_with_highlights():
    """Example 3: Search with highlighted snippets."""
    print("\n" + "=" * 60)
    print("Example 3: Search with Highlights")
    print("=" * 60)

    results = tool_web_search(
        {
            "query": "machine learning best practices",
            "num_results": 3,
            "include_text": False,
            "include_highlights": True,
        }
    )

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   {result['url']}")
        if result.get("highlights"):
            print("   Key snippets:")
            for snippet in result["highlights"][:2]:  # Show first 2
                print(f"   - {snippet[:150]}...")
        print()


def example_research_papers():
    """Example 4: Finding research papers."""
    print("\n" + "=" * 60)
    print("Example 4: Research Paper Search")
    print("=" * 60)

    results = tool_web_search(
        {
            "query": "transformer neural network architecture research papers",
            "num_results": 5,
            "include_text": True,
            "use_autoprompt": True,
        }
    )

    print(f"\nFound {len(results)} research resources:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. 📄 {result['title']}")
        print(f"   🔗 {result['url']}")
        if result.get("author"):
            print(f"   ✍️  {result['author']}")
        if result.get("published_date"):
            print(f"   📅 {result['published_date']}")
        print(f"   ⭐ Score: {result['score']:.4f}")
        print()


def example_technical_documentation():
    """Example 5: Finding technical documentation."""
    print("\n" + "=" * 60)
    print("Example 5: Technical Documentation Search")
    print("=" * 60)

    results = tool_web_search(
        {
            "query": "FastAPI authentication middleware documentation",
            "num_results": 3,
            "include_text": True,
        }
    )

    for result in results:
        print(f"\n📚 {result['title']}")
        print(f"🔗 {result['url']}")
        if result.get("text"):
            # Extract code-looking sections (simple heuristic)
            text = result["text"]
            if "def " in text or "class " in text or "import " in text:
                print("💻 Contains code examples")
        print()


def example_full_result_structure():
    """Example 6: Show complete result structure."""
    print("\n" + "=" * 60)
    print("Example 6: Full Result Structure")
    print("=" * 60)

    results = tool_web_search(
        {
            "query": "artificial intelligence ethics",
            "num_results": 1,
            "include_text": True,
            "include_highlights": True,
        }
    )

    if results:
        print("\nComplete structure of first result:")
        print()
        pprint(results[0], width=80, depth=3)


def main():
    """Run all examples."""
    # Check for API key
    if not os.getenv("EXA_API_KEY"):
        print("\n EXA_API_KEY environment variable not set!")
        print("Get your API key at: https://exa.ai")
        print("\nSet it with:")
        print("  export EXA_API_KEY='your-api-key-here'")
        return

    print("\n" + "=" * 60)
    print("Exa Web Search Tool - Examples")
    print("=" * 60)

    try:
        # Run examples
        example_basic_search()
        example_search_with_content()
        example_search_with_highlights()
        example_research_papers()
        example_technical_documentation()
        example_full_result_structure()

        print("\n" + "=" * 60)
        print("Examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
