import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import dspy
from src.evaluation.config import settings

@dataclass
class FundSearchExample:
    """Single evaluation example for fund search."""
    id: int
    query: str
    expected_intents: List[str]
    expected_extraction: dict
    expected_response_type: str
    evaluation_type: str
    why_tricky: str
    tier: int
    category: str
    
    # Optional fields
    ground_truth_cnpjs: Optional[List[str]] = None
    ground_truth_note: Optional[str] = None
    must_include_any: Optional[bool] = None
    min_results: Optional[int] = None
    expected_language: Optional[str] = None
    expected_search_query_contains: Optional[List[str]] = None
    expected_required_name_terms: Optional[List[str]] = None
    expected_ambiguous: Optional[bool] = None
    expected_context_status: Optional[str] = None
    history_context: Optional[str] = None

    # Legacy fields mapping (computed property or just ignored)
    @property
    def expected_criteria(self) -> dict:
        return self.expected_extraction

def load_main_dataset() -> List[FundSearchExample]:
    """Load the main 300-query evaluation dataset."""
    data_path = Path(settings.DATA_DIR) / "fund_search_evaluation_300.jsonl"
    if not data_path.exists():
        raise FileNotFoundError(f"Main dataset not found at {data_path}")
        
    examples = []
    with open(data_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                example = FundSearchExample(
                    id=data.get("id", line_num),
                    query=data["query"],
                    expected_intents=data.get("expected_intents", []),
                    expected_extraction=data.get("expected_extraction", {}),
                    expected_response_type=data.get("expected_response_type", ""),
                    evaluation_type=data.get("evaluation_type", ""),
                    why_tricky=data.get("why_tricky", ""),
                    tier=data.get("tier", 0),
                    category=data.get("category", ""),
                    
                    ground_truth_cnpjs=data.get("ground_truth_cnpjs"),
                    ground_truth_note=data.get("ground_truth_note"),
                    must_include_any=data.get("must_include_any"),
                    min_results=data.get("min_results"),
                    expected_language=data.get("expected_language"),
                    expected_search_query_contains=data.get("expected_search_query_contains"),
                    expected_required_name_terms=data.get("expected_required_name_terms"),
                    expected_ambiguous=data.get("expected_ambiguous"),
                    expected_context_status=data.get("expected_context_status"),
                    history_context=data.get("history_context")
                )
                examples.append(example)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Error parsing {data_path}:{line_num} - {e}")
                continue
    return examples

def get_intent_examples(train_ratio: float = 0.8) -> tuple[list[dspy.Example], list[dspy.Example]]:
    """
    Get examples suitable for IntentClassifier optimization using the main dataset.
    """
    examples = load_main_dataset()
    dspy_examples = []
    
    for ex in examples:
        # Filter out examples that are purely informational or greetings if we want to focus on search
        # But 'informational' is a valid intent, so we keep it.
        
        dspy_ex = dspy.Example(
            query=ex.query,
            expected_intents=ex.expected_intents
        ).with_inputs("query")
        dspy_examples.append(dspy_ex)

    # Simple deterministic split
    split_idx = int(len(dspy_examples) * train_ratio)
    return dspy_examples[:split_idx], dspy_examples[split_idx:]

def get_extractor_examples(train_ratio: float = 0.8) -> tuple[list[dspy.Example], list[dspy.Example]]:
    """
    Get examples suitable for SpecializedExtractor optimization using the main dataset.
    """
    examples = load_main_dataset()
    dspy_examples = []
    
    for ex in examples:
        # Only use examples where extraction is the primary evaluation type OR we have expected extraction data
        if not ex.expected_extraction and ex.evaluation_type != "extraction_match":
            continue
            
        if not ex.expected_extraction:
            # Skip empty extractions if we are training extractor? 
            # Maybe we want to train it to extract nothing for vague queries?
            # For now, let's include empty extractions as valid negative examples
            pass

        dspy_ex = dspy.Example(
            query=ex.query,
            expected_criteria=ex.expected_extraction
        ).with_inputs("query")
        dspy_examples.append(dspy_ex)

    split_idx = int(len(dspy_examples) * train_ratio)
    return dspy_examples[:split_idx], dspy_examples[split_idx:]
