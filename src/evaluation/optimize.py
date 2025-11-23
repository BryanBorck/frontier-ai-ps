"""Optimization script using GEPA optimizer.

This script runs GEPA optimization to improve system prompts.
Requires: pip install gepa
"""

import json
import os

import dspy
import mlflow
from dotenv import load_dotenv

# Import evaluation utilities from evaluate.py
from evaluation.evaluate import criteria_match_score, evaluate_parser
from evaluation.fund_search_eval_dataset import load_current_schema_examples
from src.utils.env import validate_env

# Load environment
load_dotenv()


def main():
    """Run GEPA optimization."""
    # Check if gepa is installed
    try:
        import gepa  # noqa: F401
    except ImportError:
        print("=" * 80)
        print("ERROR: GEPA package not installed")
        print("=" * 80)
        print("\nInstall GEPA with:")
        print("  uv pip install gepa")
        print("\nOr:")
        print("  pip install gepa")
        print("\n" + "=" * 80)
        return

    print("=" * 80)
    print("OPTIMIZING FUND SEARCH SYSTEM WITH GEPA")
    print("=" * 80)

    # Get config
    config = validate_env()

    # Configure DSPy
    lm = dspy.LM(model="openai/gpt-4.1-mini", api_key=config.openai_api_key)
    dspy.configure(lm=lm)

    # Load current schema examples only (103 queries that work now)
    current_examples = load_current_schema_examples()

    # Convert to DSPy format
    all_examples = []
    for ex in current_examples:
        dspy_ex = dspy.Example(
            query=ex.query,
            expected_criteria=ex.expected_criteria,
        ).with_inputs("query")
        all_examples.append(dspy_ex)

    # Split into train/test
    train_ratio = 0.8
    split_idx = int(len(all_examples) * train_ratio)
    train_examples = all_examples[:split_idx]
    test_examples = all_examples[split_idx:]

    print("\nDataset (Current Schema Only):")
    print(f"  Total examples: {len(all_examples)}")
    print(f"  Training examples: {len(train_examples)}")
    print(f"  Test examples: {len(test_examples)}")

    # Check if MLflow is enabled
    mlflow_enabled = os.getenv("MLFLOW_ENABLED", "false").lower() == "true"

    # Define metric for GEPA (new API requires 5 arguments)
    def metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
        """Metric for GEPA optimization.

        Args:
            gold: Gold/expected example
            pred: Predicted output from module
            trace: Execution trace (optional)
            pred_name: Name of prediction (optional)
            pred_trace: Prediction trace (optional)

        Returns:
            Score between 0.0 and 1.0
        """
        # Extract prediction dict
        if hasattr(pred, "criteria"):
            pred_dict = pred.criteria.model_dump()
        elif hasattr(pred, "model_dump"):
            pred_dict = pred.model_dump()
        else:
            pred_dict = pred

        # Get expected criteria from gold example
        expected = gold.expected_criteria if hasattr(gold, "expected_criteria") else gold

        return criteria_match_score(pred_dict, expected)

    # Initialize GEPA optimizer
    from dspy.teleprompt import GEPA

    print("\n" + "=" * 80)
    print("GEPA CONFIGURATION")
    print("=" * 80)

    # GEPA parameters (new API - can only use ONE of: auto, max_full_evals, max_metric_calls)
    auto_level = "medium"  # 'light' (fast), 'medium' (balanced), or 'heavy' (thorough)
    num_threads = 4  # Parallel threads for speed

    print(f"  Auto level: {auto_level}")
    print(f"  Threads: {num_threads}")
    print(f"  MLflow tracking: {'ENABLED' if mlflow_enabled else 'DISABLED'}")
    print("\n  'medium' auto level provides:")
    print("    - Balanced optimization (not too fast, not too slow)")
    print("    - Good accuracy improvement")
    print("    - ~5-10 minutes estimated time")

    print("\nInitializing GEPA optimizer...")

    # Create reflection LM (stronger model for proposing improvements)
    reflection_lm = dspy.LM(
        model="openai/gpt-4o", api_key=config.openai_api_key, temperature=1.0, max_tokens=4000
    )

    gepa_optimizer = GEPA(
        metric=metric,
        auto=auto_level,
        num_threads=num_threads,
        reflection_lm=reflection_lm,
        use_mlflow=mlflow_enabled,
        track_stats=True,
    )

    # Initialize unoptimized module
    from src.tools.tool_parse_query.module_pipeline import ParseQueryModule

    unoptimized_module = ParseQueryModule()

    # Evaluate baseline
    print("\n" + "=" * 80)
    print("BASELINE EVALUATION")
    print("=" * 80)

    class BaselineParser:
        def __init__(self, module):
            self.module = module

        def parse(self, query):
            return self.module(query=query)

    baseline_parser = BaselineParser(unoptimized_module)
    baseline_results = evaluate_parser(baseline_parser, test_examples)

    print(f"Baseline Average Score: {baseline_results['avg_score']:.2%}")

    # Run optimization
    print("\n" + "=" * 80)
    print("RUNNING GEPA OPTIMIZATION")
    print("=" * 80)
    print("\nThis may take several minutes...")
    print("GEPA will:")
    print("  1. Sample system trajectories (reasoning, tool calls, outputs)")
    print("  2. Reflect on failures in natural language")
    print("  3. Propose improved prompts")
    print("  4. Test and combine the best variations")
    print("\nProgress will be shown below:")
    print("-" * 80)

    optimized_module = gepa_optimizer.compile(
        student=unoptimized_module, trainset=train_examples, valset=test_examples
    )

    # Evaluate optimized module
    print("\n" + "=" * 80)
    print("EVALUATING OPTIMIZED MODULE")
    print("=" * 80)

    class OptimizedParser:
        def __init__(self, module):
            self.module = module

        def parse(self, query):
            return self.module(query=query)

    optimized_parser = OptimizedParser(optimized_module)
    optimized_results = evaluate_parser(optimized_parser, test_examples)

    # Print comparison
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)

    baseline_score = baseline_results["avg_score"]
    optimized_score = optimized_results["avg_score"]
    improvement = optimized_score - baseline_score

    print(f"\nBaseline Score:  {baseline_score:.2%}")
    print(f"Optimized Score: {optimized_score:.2%}")
    print(f"Improvement:     {improvement:+.2%}")

    if improvement > 0:
        print(f"\n✓ GEPA improved performance by {improvement:.2%}!")
    elif improvement == 0:
        print("\n- No improvement (already at optimal performance)")
    else:
        print(f"\n⚠ Performance decreased by {abs(improvement):.2%}")

    # Log to MLflow (if not already logged by GEPA)
    if mlflow_enabled and not gepa_optimizer.use_mlflow:
        print("\n" + "=" * 80)
        print("LOGGING TO MLFLOW")
        print("=" * 80)

        mlflow.set_experiment("FundSearch-Evaluation")

        with mlflow.start_run(run_name="gepa-optimized"):
            # Log metrics
            mlflow.log_metric("avg_score", optimized_score)
            mlflow.log_metric("baseline_score", baseline_score)
            mlflow.log_metric("improvement", improvement)
            mlflow.log_metric("num_test_examples", optimized_results["num_examples"])

            # Log parameters
            mlflow.log_param("model", "gpt-4.1-mini")
            mlflow.log_param("optimizer", "GEPA")
            mlflow.log_param("auto_level", auto_level)
            mlflow.log_param("num_threads", num_threads)
            mlflow.log_param("train_size", len(train_examples))
            mlflow.log_param("test_size", len(test_examples))

            # Log detailed results
            results_path = "gepa_optimized_results.json"
            with open(results_path, "w") as f:
                json.dump(
                    {
                        "baseline": baseline_results["results"],
                        "optimized": optimized_results["results"],
                        "improvement": improvement,
                    },
                    f,
                    indent=2,
                )

            mlflow.log_artifact(results_path)
            os.remove(results_path)

            # Save optimized module
            print("\nSaving optimized module...")
            optimized_module.save("optimized_parser_module")
            mlflow.log_artifact("optimized_parser_module")

        print("✓ Logged to MLflow")

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "src/mlflow/mlflow.db")
        print(f"\nView results at: {tracking_uri}")
    elif mlflow_enabled:
        print("\n✓ MLflow tracking was handled by GEPA")
        print("View results at: mlflow ui")

    print("\n" + "=" * 80)
    print("OPTIMIZATION COMPLETE!")
    print("=" * 80)

    return optimized_results


if __name__ == "__main__":
    main()
