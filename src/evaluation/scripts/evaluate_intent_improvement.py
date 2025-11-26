import dspy
from dspy.evaluate import Evaluate

import mlflow
from src.agent.fund_search.modules.intent import IntentClassifier
from src.evaluation.config import settings
from src.evaluation.core.dataset import get_intent_examples
from src.evaluation.core.metrics import intent_match_score


def evaluate_improvement():
    print("=" * 80)
    print("EVALUATING INTENT CLASSIFIER IMPROVEMENT")
    print("=" * 80)

    # 0. Configure LM
    lm = dspy.LM(model=settings.DEFAULT_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.0)
    dspy.configure(lm=lm)
    print(f"Configured LM: {settings.DEFAULT_MODEL}")

    # 1. Prepare Data
    _, val_set = get_intent_examples()
    print(f"Validation Set Size: {len(val_set)}")

    # 2. Define Metric
    def intent_metric(gold, pred, trace=None):
        return intent_match_score(pred.intents, gold.expected_intents)

    # 3. Setup Evaluator
    evaluator = Evaluate(
        devset=val_set, metric=intent_metric, num_threads=4, display_progress=True, display_table=0
    )

    # 4. Evaluate Baseline (Current Code)
    print("\nEvaluating Baseline (Current Code)...")
    baseline_module = IntentClassifier()
    # Evaluate returns a float in most versions, but let's be safe
    baseline_result = evaluator(baseline_module)

    # Handle potential object return
    if hasattr(baseline_result, "score"):
        baseline_score = baseline_result.score
    print(f"Baseline Score: {baseline_score}")

    # 5. Evaluate Optimized (Loaded from JSON)
    print("\nEvaluating Optimized Module...")
    optimized_module = IntentClassifier()
    optimized_path = "src/evaluation/results/optimized_intent_classifier.json"

    try:
        optimized_module.load(optimized_path)
        optimized_result = evaluator(optimized_module)

        if hasattr(optimized_result, "score"):
            optimized_score = optimized_result.score
        else:
            optimized_score = optimized_result

        print(f"Optimized Score: {optimized_score}")

        improvement = optimized_score - baseline_score
        print(f"\nImprovement: {improvement:+.2f}")

        # 6. Log to MLflow
        if settings.MLFLOW_ENABLED:
            mlflow.set_experiment(f"{settings.MLFLOW_EXPERIMENT_NAME}-Evaluation")
            with mlflow.start_run(run_name="Intent-Improvement-Check"):
                mlflow.log_metric("baseline_accuracy", baseline_score)
                mlflow.log_metric("optimized_accuracy", optimized_score)
                mlflow.log_metric("improvement", improvement)
                print("Logged results to MLflow.")

    except Exception as e:
        print(f"Error loading optimized module: {e}")
        optimized_score = 0.0


if __name__ == "__main__":
    evaluate_improvement()
