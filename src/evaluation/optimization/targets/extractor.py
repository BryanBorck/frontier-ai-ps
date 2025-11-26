import dspy

from src.agent.fund_search.modules.extraction import SpecializedExtractor
from src.evaluation.core.dataset import get_extractor_examples
from src.evaluation.core.metrics import criteria_match_score
from src.evaluation.optimization.optimizer import GepaOptimizer


def optimize_extractor(auto_level="medium", num_threads=4):
    """
    Optimize the SpecializedExtractor module.
    """
    print("=" * 80)
    print("OPTIMIZING SPECIALIZED EXTRACTOR")
    print("=" * 80)

    # 1. Prepare Data
    train_set, val_set = get_extractor_examples()
    print(f"Data: {len(train_set)} train, {len(val_set)} val")

    # 2. Define Module
    # Note: Extractor usually needs intents as input.
    # In this optimization loop, we assume the input example has 'query'.
    # But SpecializedExtractor signature needs intents.
    # We might need to wrap it or provide intents in the example inputs.
    # For now, let's assume we optimize it assuming 'find_by_criteria' intent for all these examples.

    class ExtractorWrapper(dspy.Module):
        def __init__(self):
            super().__init__()
            self.extractor = SpecializedExtractor()

        def forward(self, query):
            # Hardcode intent for pure extractor optimization on criteria dataset
            # Use "find_by_criteria" to trigger the ExtractCriteriaSignature chain
            return self.extractor(query=query, intents=["find_by_criteria"])

    module = ExtractorWrapper()

    # 3. Define Metric Adapter
    def extractor_metric(gold, pred, trace=None, pred_name=None, pred_trace=None, **kwargs):
        # pred is dspy.Prediction(parsed_query=ParsedQuery(...))
        if hasattr(pred, "parsed_query"):
            pred_dict = pred.parsed_query.to_dict()
        else:
            pred_dict = {}
        return criteria_match_score(pred_dict, gold.expected_criteria)

    # 4. Run Optimizer
    optimizer = GepaOptimizer(
        metric_fn=extractor_metric, auto_level=auto_level, num_threads=num_threads
    )

    optimized_module = optimizer.optimize(
        module=module, trainset=train_set, valset=val_set, experiment_name_suffix="Extractor"
    )

    # 5. Save
    output_dir = "src/evaluation/results"
    import os

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "optimized_extractor.json")
    optimized_module.save(output_path)
    print(f"\nSaved optimized module to {output_path}")

    return optimized_module
