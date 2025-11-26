def intent_match_score(predicted_intents: list[str], expected_intents: list[str]) -> float:
    """
    Calculate accuracy of intent classification.
    Returns 1.0 if the primary expected intent is found in predicted intents, else 0.0.
    """
    if not expected_intents:
        return 1.0 # No expectation, pass
    
    # Check if primary expected intent is in predicted
    # We assume the first expected intent is the primary one
    primary_expected = expected_intents[0]
    
    if primary_expected in predicted_intents:
        return 1.0
    
    return 0.0

def criteria_match_score(predicted: dict, expected: dict) -> float:
    """
    Calculate how well predicted criteria matches expected criteria (F1-like or Accuracy).
    """
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
        if field not in expected:
            continue

        expected_val = expected[field]
        if expected_val is None:
            continue

        total += 1
        predicted_val = predicted.get(field)

        # Handle Enum or Pydantic serialization differences
        if hasattr(predicted_val, "value"):
            predicted_val = predicted_val.value
            
        # Normalization for string comparison
        if isinstance(predicted_val, str) and isinstance(expected_val, str):
            if predicted_val.lower() == expected_val.lower():
                matches += 1
                continue

        if predicted_val == expected_val:
            matches += 1

    return matches / total if total > 0 else 1.0

