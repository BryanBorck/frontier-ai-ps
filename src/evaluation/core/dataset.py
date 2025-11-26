import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import dspy
from src.evaluation.config import settings

@dataclass
class FundSearchExample:
    """Single evaluation example for fund search."""
    query: str
    expected_criteria: dict
    expected_fund_cnpjs: list[str] | None = None
    description: str = ""
    category: str = ""
    eval_category: str = ""
    validation_type: str = ""

def load_examples_from_jsonl(data_dir: Path | None = None) -> list[FundSearchExample]:
    """Load examples from JSONL files in the data directory."""
    if data_dir is None:
        data_dir = Path(settings.DATA_DIR)

    examples = []
    # Recursively find all .jsonl files
    jsonl_files = sorted(data_dir.rglob("*.jsonl"))

    for jsonl_file in jsonl_files:
        with open(jsonl_file) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
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

def get_current_schema_examples() -> list[FundSearchExample]:
    """Load examples that work with current schema."""
    data_dir = Path(settings.DATA_DIR) / "_current_schema"
    return load_examples_from_jsonl(data_dir)

def get_intent_examples(train_ratio: float = 0.8) -> tuple[list[dspy.Example], list[dspy.Example]]:
    """
    Get examples suitable for IntentClassifier optimization.
    Derives expected intents from category or eval_category if not explicitly present.
    """
    examples = get_current_schema_examples()
    dspy_examples = []
    
    for ex in examples:
        intents = []
        
        # Heuristic mapping based on evaluation categories
        # See src/agent/fund_search/signatures/intent.py for valid intents
        
        # 1. find_by_name / find_by_strategy (Semantic Search)
        if ex.category == "basic_company" or "single_company" in str(ex.eval_category):
             intents = ["find_by_strategy"] # Company names often need semantic strategy search ("funds from Itau")
        elif "exact_match" in str(ex.eval_category):
             intents = ["find_by_name"] # Specific fund name

        # 2. find_by_criteria (Structured DB Search)
        elif "criteria" in str(ex.eval_category) or "single_" in str(ex.eval_category):
             # single_asset_class, single_geographic, dual_criteria -> find_by_criteria
             # EXCEPT if it's about holdings (exposure)
             intents = ["find_by_criteria"]
        
        # 3. ranking_sorting
        elif "ranking" in str(ex.eval_category):
            # "top 10 funds" -> has_numeric_filter + find_by_criteria?
            # Or just find_by_criteria with sort?
            # The intent classifier usually outputs 'has_numeric_filter' for "top N"
            intents = ["has_numeric_filter", "find_by_criteria"]

        # 4. browse_general
        elif "browse" in str(ex.eval_category):
            intents = ["general_browse"]

        # Fallback based on criteria presence
        if not intents:
             if ex.expected_criteria and any(ex.expected_criteria.values()):
                 intents = ["find_by_criteria"]
             else:
                 intents = ["informational"] 

        dspy_ex = dspy.Example(
            query=ex.query,
            expected_intents=intents
        ).with_inputs("query")
        dspy_examples.append(dspy_ex)

    split_idx = int(len(dspy_examples) * train_ratio)
    return dspy_examples[:split_idx], dspy_examples[split_idx:]

def get_extractor_examples(train_ratio: float = 0.8) -> tuple[list[dspy.Example], list[dspy.Example]]:
    """
    Get examples suitable for SpecializedExtractor optimization.
    Only includes examples relevant for extraction (find_by_criteria).
    """
    examples = get_current_schema_examples()
    dspy_examples = []
    
    for ex in examples:
        # Skip examples that have no expected criteria (e.g. pure semantic search)
        if not ex.expected_criteria and not ex.expected_fund_cnpjs:
            continue

        # Extractor needs the query and the expected structured criteria
        dspy_ex = dspy.Example(
            query=ex.query,
            expected_criteria=ex.expected_criteria
        ).with_inputs("query")
        dspy_examples.append(dspy_ex)

    split_idx = int(len(dspy_examples) * train_ratio)
    return dspy_examples[:split_idx], dspy_examples[split_idx:]
