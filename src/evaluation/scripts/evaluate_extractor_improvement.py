import dspy
import mlflow
from src.agent.fund_search.modules.extraction import SpecializedExtractor
from src.evaluation.core.dataset import get_extractor_examples
from src.evaluation.core.metrics import criteria_match_score
from src.evaluation.config import settings
from dspy.evaluate import Evaluate

def evaluate_extractor_improvement():
    print("=" * 80)
    print("EVALUATING EXTRACTOR IMPROVEMENT")
    print("=" * 80)

    # 0. Configure LM
    lm = dspy.LM(
        model=settings.DEFAULT_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.0
    )
    dspy.configure(lm=lm)
    print(f"Configured LM: {settings.DEFAULT_MODEL}")

    # 1. Prepare Data
    # Use 50% split to match intent evaluation strategy for more robust validation
    _, val_set = get_extractor_examples(train_ratio=0.5)
    print(f"Validation Set Size: {len(val_set)}")

    # 2. Define Metric
    def extractor_metric(gold, pred, trace=None):
        # pred is dspy.Prediction(parsed_query=ParsedQuery(...))
        if hasattr(pred, "parsed_query"):
            pred_dict = pred.parsed_query.to_dict()
        else:
            pred_dict = {}
        return criteria_match_score(pred_dict, gold.expected_criteria)

    # 3. Setup Evaluator
    evaluator = Evaluate(
        devset=val_set, 
        metric=extractor_metric, 
        num_threads=4, 
        display_progress=True, 
        display_table=0
    )

    class ExtractorWrapper(dspy.Module):
        def __init__(self):
            super().__init__()
            self.extractor = SpecializedExtractor()

        def forward(self, query):
            # Hardcode intent to trigger criteria extraction for apples-to-apples comparison
            # We are optimizing/evaluating extraction capability, assuming intent is known.
            return self.extractor(query=query, intents=["find_by_criteria"])

    # 4. Evaluate Baseline (Current Code)
    print("\nEvaluating Baseline (Current Code)...")
    baseline_module = ExtractorWrapper()
    
    baseline_result = evaluator(baseline_module)
    if hasattr(baseline_result, "score"):
        baseline_score = baseline_result.score
    else:
        baseline_score = baseline_result
        
    print(f"Baseline Score: {baseline_score}")

    # 5. Evaluate Optimized (Loaded from JSON)
    print("\nEvaluating Optimized Module...")
    optimized_module = ExtractorWrapper()
    # We need to load the optimized sub-module (SpecializedExtractor)
    optimized_path = "src/evaluation/results/optimized_extractor.json"
    
    try:
        # Load into the wrapper since the optimization was run on the wrapper
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
            with mlflow.start_run(run_name="Extractor-Improvement-Check"):
                mlflow.log_metric("baseline_accuracy", baseline_score)
                mlflow.log_metric("optimized_accuracy", optimized_score)
                mlflow.log_metric("improvement", improvement)
                print("Logged results to MLflow.")
                
    except Exception as e:
        print(f"Error loading optimized module (file might not exist yet): {e}")
        optimized_score = 0.0

if __name__ == "__main__":
    evaluate_extractor_improvement()

