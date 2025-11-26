import argparse
from src.evaluation.optimization.targets.intent import optimize_intent
from src.evaluation.optimization.targets.extractor import optimize_extractor
from src.evaluation.optimization.targets.rewriter import optimize_rewriter

def main():
    parser = argparse.ArgumentParser(description="Run GEPA optimization.")
    parser.add_argument("--target", required=True, choices=["intent", "extractor", "rewriter"], help="Module to optimize")
    parser.add_argument("--auto", default="medium", help="GEPA auto level (light, medium, heavy)")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    
    args = parser.parse_args()
    
    if args.target == "intent":
        optimize_intent(auto_level=args.auto, num_threads=args.threads)
    elif args.target == "extractor":
        optimize_extractor(auto_level=args.auto, num_threads=args.threads)
    elif args.target == "rewriter":
        optimize_rewriter(auto_level=args.auto, num_threads=args.threads)

if __name__ == "__main__":
    main()

