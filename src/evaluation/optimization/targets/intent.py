from src.agent.fund_search.modules.intent import IntentClassifier
from src.evaluation.core.dataset import get_intent_examples
from src.evaluation.core.metrics import intent_match_score
from src.evaluation.optimization.optimizer import GepaOptimizer


def optimize_intent(auto_level="medium", num_threads=4):
    """
    Optimize the IntentClassifier module.
    """
    print("=" * 80)
    print("OPTIMIZING INTENT CLASSIFIER")
    print("=" * 80)

    # 1. Prepare Data
    train_set, val_set = get_intent_examples()
    print(f"Data: {len(train_set)} train, {len(val_set)} val")

    # 2. Define Module
    module = IntentClassifier()

    # 3. Define Metric Adapter
    def intent_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
        return intent_match_score(pred.intents, gold.expected_intents)

    # 4. Run Optimizer
    optimizer = GepaOptimizer(
        metric_fn=intent_metric, auto_level=auto_level, num_threads=num_threads
    )

    optimized_module = optimizer.optimize(
        module=module, trainset=train_set, valset=val_set, experiment_name_suffix="Intent"
    )

    # 5. Save
    output_dir = "src/evaluation/results"
    import os

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "optimized_intent_classifier.json")
    optimized_module.save(output_path)
    print(f"\nSaved optimized module to {output_path}")

    return optimized_module
