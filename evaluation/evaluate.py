"""Evaluation script for fund search system.

This script evaluates the current system on the test dataset and logs metrics to MLflow.
"""

import json
import os
from typing import Any

import dspy
import mlflow
from dotenv import load_dotenv

from evaluation.fund_search_eval_dataset import get_train_test_split
from src.tools.tool_parse_query.index import _FundQueryParserInternal
from src.utils.env import validate_env

# Load environment
load_dotenv()


def criteria_match_score(predicted: dict, expected: dict) -> float:
    """Calculate how well predicted criteria matches expected criteria.

    Args:
        predicted: Predicted fund search criteria
        expected: Expected fund search criteria

    Returns:
        Score between 0.0 and 1.0 (1.0 = perfect match)
    """
    # Fields to compare
    fields = [
        "fund_legal_name",
        "fund_type",
        "investment_class",
        "fund_of_funds",
        "target_audience",
        "manager_type",
        "is_exclusive_fund",
        "can_invest_abroad_100_pct",
        "has_long_term_taxation",
    ]

    matches = 0
    total = 0

    for field in fields:
        # Only count fields that are set in expected
        if field not in expected:
            continue

        expected_val = expected[field]

        # Skip None values in expected (we don't care about these)
        if expected_val is None:
            continue

        total += 1
        predicted_val = predicted.get(field)

        # Check for match (handle enum values)
        if hasattr(predicted_val, "value"):
            predicted_val = predicted_val.value

        if predicted_val == expected_val:
            matches += 1

    # Return score (handle case where no fields to compare)
    return matches / total if total > 0 else 1.0


def evaluate_parser(parser: Any, test_examples: list[dspy.Example]) -> dict:
    """Evaluate the parser on test examples.

    Args:
        parser: Parser module to evaluate
        test_examples: List of test examples

    Returns:
        Dictionary with evaluation metrics
    """
    total_score = 0.0
    num_examples = len(test_examples)

    results = []

    for ex in test_examples:
        # Parse the query
        predicted = parser.parse(ex.query)

        # Convert to dict if it's a Pydantic model
        predicted_dict = predicted.model_dump() if hasattr(predicted, "model_dump") else predicted

        # Calculate score
        score = criteria_match_score(predicted_dict, ex.expected_criteria)
        total_score += score

        results.append(
            {
                "query": ex.query,
                "expected": ex.expected_criteria,
                "predicted": predicted_dict,
                "score": score,
            }
        )

    avg_score = total_score / num_examples

    return {
        "avg_score": avg_score,
        "total_score": total_score,
        "num_examples": num_examples,
        "results": results,
    }


def main():
    """Evaluate the current system and log results to MLflow."""
    print("=" * 80)
    print("EVALUATING FUND SEARCH SYSTEM")
    print("=" * 80)

    # Get config
    config = validate_env()

    # Configure DSPy
    lm = dspy.LM(model="openai/gpt-4.1-mini", api_key=config.openai_api_key)
    dspy.configure(lm=lm)

    # Get train/test split
    train_examples, test_examples = get_train_test_split(train_ratio=0.8)

    print("\nDataset split:")
    print(f"  Training examples: {len(train_examples)}")
    print(f"  Test examples: {len(test_examples)}")

    # Initialize parser
    print("\nInitializing parser...")
    parser = _FundQueryParserInternal()

    # Evaluate on test set
    print("\nEvaluating parser on test set...")
    eval_results = evaluate_parser(parser, test_examples)

    print(f"\n{'=' * 80}")
    print("RESULTS")
    print(f"{'=' * 80}")
    print(f"Average Score: {eval_results['avg_score']:.2%}")
    print(f"Total Examples: {eval_results['num_examples']}")
    print(f"Total Score: {eval_results['total_score']:.1f}/{eval_results['num_examples']}")

    # Print detailed results
    print(f"\n{'=' * 80}")
    print("DETAILED RESULTS")
    print(f"{'=' * 80}")

    perfect_count = 0
    for i, result in enumerate(eval_results["results"], 1):
        score = result["score"]
        if score == 1.0:
            perfect_count += 1

        print(f"\n{i}. {result['query']}")
        print(f"   Score: {score:.0%}")

        if score < 1.0:
            print(f"   Expected: {result['expected']}")
            print(f"   Predicted: {result['predicted']}")

    print(f"\n{'=' * 80}")
    print(f"Perfect matches: {perfect_count}/{eval_results['num_examples']}")
    print(f"{'=' * 80}")

    # Log to MLflow
    mlflow_enabled = os.getenv("MLFLOW_ENABLED", "false").lower() == "true"

    if mlflow_enabled:
        print("\nLogging to MLflow...")
        mlflow.set_experiment("FundSearch-Evaluation")

        with mlflow.start_run(run_name="baseline-evaluation"):
            # Log metrics
            mlflow.log_metric("avg_score", eval_results["avg_score"])
            mlflow.log_metric("num_test_examples", eval_results["num_examples"])
            mlflow.log_metric("perfect_matches", perfect_count)

            # Log parameters
            mlflow.log_param("model", "gpt-4.1-mini")
            mlflow.log_param("test_size", len(test_examples))
            mlflow.log_param("train_size", len(train_examples))
            mlflow.log_param("optimizer", "none")

            # Log detailed results as artifact
            results_path = "eval_results.json"
            with open(results_path, "w") as f:
                json.dump(eval_results["results"], f, indent=2)

            mlflow.log_artifact(results_path)
            os.remove(results_path)

        print("✓ Logged to MLflow")

        # Print MLflow info
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
        print(f"\nView results at: {tracking_uri}")

    return eval_results


if __name__ == "__main__":
    main()
