import argparse
import sys
from src.evaluation.core.dataset import get_intent_examples, get_extractor_examples
from src.evaluation.core.pipeline import FundExtractionPipeline
from src.evaluation.core.metrics import intent_match_score, criteria_match_score
from src.agent.fund_search.modules.intent import IntentClassifier
from src.agent.fund_search.modules.extraction import SpecializedExtractor

def run_evaluate_intent():
    print("Evaluating IntentClassifier...")
    _, test_set = get_intent_examples()
    module = IntentClassifier()
    
    total = 0
    correct = 0
    for ex in test_set:
        pred = module(query=ex.query)
        score = intent_match_score(pred.intents, ex.expected_intents)
        correct += score
        total += 1
        print(f"Query: {ex.query[:50]}... -> Pred: {pred.intents} / Exp: {ex.expected_intents} (Score: {score})")
        
    print(f"Accuracy: {correct/total:.2%}")

def run_evaluate_extractor():
    print("Evaluating SpecializedExtractor...")
    _, test_set = get_extractor_examples()
    # For standalone eval, we need to know intents. We'll cheat and say 'find_by_criteria'
    module = SpecializedExtractor()
    
    total_score = 0
    count = 0
    for ex in test_set:
        # Pass dummy intent
        pred = module(query=ex.query, intents=["find_by_criteria"])
        
        pred_dict = pred.parsed_query.to_dict()
        score = criteria_match_score(pred_dict, ex.expected_criteria)
        total_score += score
        count += 1
        
    print(f"Avg Criteria Match Score: {total_score/count:.2%}")

def run_evaluate_pipeline():
    print("Evaluating Full Pipeline (Intent + Extractor)...")
    # We need a dataset that has BOTH intent and criteria?
    # Our dataset has criteria, we can check that.
    _, test_set = get_extractor_examples()
    module = FundExtractionPipeline()
    
    total_score = 0
    count = 0
    for ex in test_set:
        pred = module(query=ex.query) # Returns dspy.Prediction(intents=..., criteria=...)
        
        # Evaluate criteria match (end-to-end extraction performance)
        pred_dict = pred.criteria.to_dict()
        score = criteria_match_score(pred_dict, ex.expected_criteria)
        total_score += score
        count += 1
        
    print(f"Pipeline Avg Score: {total_score/count:.2%}")

def main():
    parser = argparse.ArgumentParser(description="Run evaluations.")
    parser.add_argument("mode", choices=["intent", "extractor", "pipeline"], help="Component to evaluate")
    args = parser.parse_args()
    
    if args.mode == "intent":
        run_evaluate_intent()
    elif args.mode == "extractor":
        run_evaluate_extractor()
    elif args.mode == "pipeline":
        run_evaluate_pipeline()

if __name__ == "__main__":
    main()

