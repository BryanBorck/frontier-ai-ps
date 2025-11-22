"""Evaluation dataset for fund search system.

This dataset contains example queries with expected outputs for evaluating
and optimizing the DSPy ReAct agent using GEPA and other optimizers.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import dspy


@dataclass
class FundSearchExample:
    """Single evaluation example for fund search."""

    query: str  # User's natural language query
    expected_criteria: dict  # Expected parsed criteria
    expected_fund_cnpjs: list[str] | None = None  # Expected fund CNPJs (optional)
    description: str = ""  # Human-readable description of what this tests
    category: str = ""  # Original category (topic-based)
    eval_category: str = ""  # Evaluation category (criteria-based)
    validation_type: str = ""  # How to validate: exact_match, contains, criteria_match, ordered


def load_examples_from_jsonl(data_dir: Path | None = None) -> list[FundSearchExample]:
    """Load examples from JSONL files in the data directory.

    Args:
        data_dir: Path to data directory (defaults to evaluation/data/)

    Returns:
        List of FundSearchExample objects
    """
    if data_dir is None:
        data_dir = Path(__file__).parent / "data"

    examples = []

    # Find all .jsonl files recursively
    jsonl_files = sorted(data_dir.rglob("*.jsonl"))

    for jsonl_file in jsonl_files:
        with open(jsonl_file) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                try:
                    data = json.loads(line)
                    example = FundSearchExample(
                        query=data["query"],
                        expected_criteria=data["expected_criteria"],
                        expected_fund_cnpjs=data.get("expected_fund_cnpjs"),
                        description=data.get("description", ""),
                        category=data.get("category", ""),
                        eval_category=data.get("eval_category", ""),
                        validation_type=data.get("validation_type", ""),
                    )
                    examples.append(example)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Error parsing {jsonl_file}:{line_num} - {e}")
                    continue

    return examples


# Load examples from JSONL files
FUND_SEARCH_EXAMPLES = load_examples_from_jsonl()

# Legacy hardcoded examples (kept for backward compatibility)
# These will be overridden by JSONL files if they exist
_LEGACY_EXAMPLES = [
    # Basic company name queries
    FundSearchExample(
        query="give me itau funds",
        expected_criteria={
            "fund_legal_name": "itau",
            "fund_type": None,
            "investment_class": None,
            "fund_of_funds": None,
        },
        description="Basic company name extraction - Itaú",
        category="basic_company",
    ),
]

# Use JSONL examples if available, otherwise fall back to legacy
if not FUND_SEARCH_EXAMPLES:
    print("Warning: No JSONL examples found, using legacy hardcoded examples")
    FUND_SEARCH_EXAMPLES = _LEGACY_EXAMPLES


def create_dspy_examples() -> list[dspy.Example]:
    """Convert evaluation examples to DSPy Example format.

    Returns:
        List of DSPy Example objects for use with optimizers
    """
    examples = []
    for ex in FUND_SEARCH_EXAMPLES:
        # Create DSPy Example with input and expected output
        dspy_ex = dspy.Example(
            query=ex.query,
            expected_criteria=ex.expected_criteria,
        ).with_inputs("query")

        examples.append(dspy_ex)

    return examples


def get_train_test_split(train_ratio: float = 0.8) -> tuple[list[dspy.Example], list[dspy.Example]]:
    """Split dataset into train and test sets.

    Args:
        train_ratio: Ratio of examples to use for training (default: 0.8)

    Returns:
        Tuple of (train_examples, test_examples)
    """
    examples = create_dspy_examples()
    split_idx = int(len(examples) * train_ratio)

    return examples[:split_idx], examples[split_idx:]


def get_examples_by_category(category: str | None = None) -> list[FundSearchExample]:
    """Get examples filtered by category.

    Args:
        category: Category to filter by (None returns all)

    Returns:
        List of examples matching the category
    """
    if category is None:
        return FUND_SEARCH_EXAMPLES

    return [ex for ex in FUND_SEARCH_EXAMPLES if ex.category == category]


def get_examples_by_eval_category(eval_category: str | None = None) -> list[FundSearchExample]:
    """Get examples filtered by evaluation category.

    Args:
        eval_category: Evaluation category to filter by (None returns all)

    Returns:
        List of examples matching the evaluation category
    """
    if eval_category is None:
        return FUND_SEARCH_EXAMPLES

    return [ex for ex in FUND_SEARCH_EXAMPLES if ex.eval_category == eval_category]


def load_current_schema_examples() -> list[FundSearchExample]:
    """Load only examples that work with current schema (no future features).

    Returns:
        List of examples from _current_schema folder
    """
    data_dir = Path(__file__).parent / "data" / "_current_schema"
    return load_examples_from_jsonl(data_dir)


def load_future_feature_examples() -> list[FundSearchExample]:
    """Load only examples that require future features.

    Returns:
        List of examples from _future_features folder
    """
    data_dir = Path(__file__).parent / "data" / "_future_features"
    return load_examples_from_jsonl(data_dir)


def print_dataset_stats():
    """Print statistics about the dataset."""
    print("=" * 80)
    print("EVALUATION DATASET STATISTICS")
    print("=" * 80)

    # Load split datasets
    current_examples = load_current_schema_examples()
    future_examples = load_future_feature_examples()

    print(f"\nTotal examples: {len(FUND_SEARCH_EXAMPLES)}")
    print(f"  ✅ Current schema (ready to evaluate): {len(current_examples)}")
    print(f"  🔮 Future features (need implementation): {len(future_examples)}")

    # Group by eval_category (primary categorization)
    print("\n" + "=" * 80)
    print("CURRENT SCHEMA EXAMPLES (103 queries)")
    print("=" * 80)

    current_categories = {}
    for ex in current_examples:
        cat = ex.eval_category or "uncategorized"
        current_categories[cat] = current_categories.get(cat, 0) + 1

    for category, count in sorted(current_categories.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {category:30s}: {count:3d}")

    print("\n" + "=" * 80)
    print("FUTURE FEATURE EXAMPLES (157 queries)")
    print("=" * 80)

    future_categories = {}
    for ex in future_examples:
        cat = ex.eval_category or "uncategorized"
        future_categories[cat] = future_categories.get(cat, 0) + 1

    for category, count in sorted(future_categories.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {category:30s}: {count:3d}")

    # Group by validation type (current schema only)
    print("\n" + "=" * 80)
    print("VALIDATION TYPES (Current Schema)")
    print("=" * 80)

    validation_types = {}
    for ex in current_examples:
        vtype = ex.validation_type or "not_set"
        validation_types[vtype] = validation_types.get(vtype, 0) + 1

    for vtype, count in sorted(validation_types.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {vtype:30s}: {count:3d}")

    # Sample examples
    print("\n" + "=" * 80)
    print("SAMPLE QUERIES (Current Schema)")
    print("=" * 80)

    seen_cats = set()
    for ex in current_examples:
        if ex.eval_category and ex.eval_category not in seen_cats:
            seen_cats.add(ex.eval_category)
            print(f"\n[{ex.eval_category}] {ex.query}")
            print(f"  → Validation: {ex.validation_type}")
            print(f"  → Expected: {ex.expected_criteria}")
            if len(seen_cats) >= 5:  # Show first 5 categories
                break

    print("\n" + "=" * 80)
    print(f"📊 Run evaluation on {len(current_examples)} current schema queries:")
    print("   MLFLOW_ENABLED=true uv run python -m evaluation.evaluate")
    print("=" * 80)


if __name__ == "__main__":
    print_dataset_stats()
