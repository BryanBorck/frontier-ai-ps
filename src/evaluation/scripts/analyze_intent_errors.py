import dspy

from src.agent.fund_search.modules.intent import IntentClassifier
from src.evaluation.config import settings
from src.evaluation.core.dataset import get_intent_examples
from src.evaluation.core.metrics import intent_match_score


def analyze_errors():
    print("=" * 80)
    print("ANALYZING INTENT CLASSIFIER ERRORS")
    print("=" * 80)

    # 1. Configure LM
    lm = dspy.LM(model=settings.DEFAULT_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.0)
    dspy.configure(lm=lm)

    # 2. Get Data
    # We'll check the validation set to see the remaining errors
    _, val_set = get_intent_examples()
    print(f"Analyzing {len(val_set)} validation examples...\n")

    # 3. Run Module
    module = IntentClassifier()

    errors = []
    correct_count = 0

    for i, example in enumerate(val_set):
        print(f"Processing {i + 1}/{len(val_set)}...", end="\r")
        try:
            pred = module(query=example.query)
            score = intent_match_score(pred.intents, example.expected_intents)

            if score == 1.0:
                correct_count += 1
            else:
                # Capture Error Details
                errors.append(
                    {
                        "query": example.query,
                        "expected": example.expected_intents,
                        "predicted": pred.intents,
                        "reasoning": getattr(
                            pred, "reasoning", "No reasoning captured (check module structure)"
                        ),
                        "search_query": pred.search_query,
                        "ambiguous": pred.is_potentially_ambiguous,
                    }
                )
        except Exception as e:
            print(f"\nError processing query '{example.query}': {e}")

    print(
        f"\n\nAccuracy: {correct_count}/{len(val_set)} ({correct_count / len(val_set) * 100:.1f}%)"
    )
    print(f"Total Errors: {len(errors)}")

    if errors:
        print("\n" + "=" * 80)
        print("ERROR REPORT")
        print("=" * 80)

        for i, error in enumerate(errors, 1):
            print(f"\n[{i}] Query: '{error['query']}'")
            print(f"    Expected:  {error['expected']}")
            print(f"    Predicted: {error['predicted']}")
            print(
                f"    Reasoning: {error['reasoning']}"
            )  # Note: standard dspy.Prediction might not explicitly expose reasoning field unless we ensure it's passed through.
            print(f"    Generated Search: {error['search_query']}")
            print(f"    Ambiguous Flag: {error['ambiguous']}")
            print("-" * 40)


if __name__ == "__main__":
    analyze_errors()
