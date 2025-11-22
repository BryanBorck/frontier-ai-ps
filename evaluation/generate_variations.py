"""Helper script to generate variations of evaluation examples.

This script helps you quickly scale to 100+ examples by generating systematic
variations of queries with different phrasings, companies, and combinations.
"""

import json
from pathlib import Path

# Common Brazilian financial institutions
COMPANIES = [
    "itau", "btg", "bradesco", "santander", "xp", "nubank",
    "safra", "inter", "c6", "modal", "genial", "rico"
]

# Query templates with variations
QUERY_TEMPLATES = {
    "company": [
        "show me {company} funds",
        "give me {company} funds",
        "{company} funds",
        "i want {company} funds",
        "find {company} funds",
        "list {company} funds",
    ],
    "fund_type": [
        "find {fund_type} funds",
        "show me {fund_type} options",
        "i want {fund_type} funds",
        "{fund_type} funds",
        "list {fund_type} funds",
    ],
    "investment_class": [
        "show me {investment_class} funds",
        "fundos de {investment_class}",
        "{investment_class} funds",
        "i want {investment_class} funds",
    ],
}

FUND_TYPES = ["FIP", "FIDC", "FII", "ETF"]
INVESTMENT_CLASSES = ["Multimercado", "Ações", "Renda Fixa", "Cambial"]


def generate_company_examples() -> list[dict]:
    """Generate company name examples with variations."""
    examples = []
    for company in COMPANIES:
        for template in QUERY_TEMPLATES["company"]:
            query = template.format(company=company)
            examples.append({
                "query": query,
                "expected_criteria": {
                    "fund_legal_name": company,
                    "fund_type": None,
                    "investment_class": None,
                    "fund_of_funds": None,
                },
                "description": f"Basic company name extraction - {company.title()}",
                "category": "basic_company",
            })
    return examples


def generate_fund_type_examples() -> list[dict]:
    """Generate fund type examples with variations."""
    examples = []
    for fund_type in FUND_TYPES:
        for template in QUERY_TEMPLATES["fund_type"]:
            query = template.format(fund_type=fund_type)
            examples.append({
                "query": query,
                "expected_criteria": {
                    "fund_legal_name": None,
                    "fund_type": fund_type,
                    "investment_class": None,
                    "fund_of_funds": None,
                },
                "description": f"Fund type extraction - {fund_type}",
                "category": "basic_fund_type",
            })
    return examples


def generate_combined_examples() -> list[dict]:
    """Generate combined examples (company + type)."""
    examples = []
    # Sample a few combinations to avoid explosion
    combinations = [
        ("itau", "FIP"),
        ("btg", "FIP"),
        ("bradesco", "FIDC"),
        ("santander", "FII"),
        ("xp", "Multimercado", "investment_class"),
    ]

    for combo in combinations:
        if len(combo) == 2:
            company, fund_type = combo
            query = f"{company} {fund_type} funds"
            examples.append({
                "query": query,
                "expected_criteria": {
                    "fund_legal_name": company,
                    "fund_type": fund_type,
                    "investment_class": None,
                    "fund_of_funds": None,
                },
                "description": f"Combined - {company} + {fund_type}",
                "category": "combined_two",
            })
        else:
            company, value, field = combo
            query = f"{company} {value} funds"
            examples.append({
                "query": query,
                "expected_criteria": {
                    "fund_legal_name": company,
                    "fund_type": None,
                    "investment_class": value,
                    "fund_of_funds": None,
                },
                "description": f"Combined - {company} + {value}",
                "category": "combined_two",
            })

    return examples


def save_examples(examples: list[dict], filepath: Path):
    """Save examples to JSONL file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")

    print(f"✓ Saved {len(examples)} examples to {filepath}")


def main():
    """Generate example variations."""
    data_dir = Path(__file__).parent / "data"

    print("Generating example variations...")
    print("=" * 80)

    # Generate company examples
    company_examples = generate_company_examples()
    print(f"\nCompany examples: {len(company_examples)}")
    print(f"Preview: {company_examples[0]['query']}")
    save_examples(company_examples, data_dir / "basic" / "company_names_generated.jsonl")

    # Generate fund type examples
    fund_type_examples = generate_fund_type_examples()
    print(f"\nFund type examples: {len(fund_type_examples)}")
    print(f"Preview: {fund_type_examples[0]['query']}")
    save_examples(fund_type_examples, data_dir / "basic" / "fund_types_generated.jsonl")

    # Generate combined examples
    combined_examples = generate_combined_examples()
    print(f"\nCombined examples: {len(combined_examples)}")
    print(f"Preview: {combined_examples[0]['query']}")
    save_examples(combined_examples, data_dir / "combined" / "two_criteria_generated.jsonl")

    total = len(company_examples) + len(fund_type_examples) + len(combined_examples)
    print("\n" + "=" * 80)
    print(f"Total generated: {total} examples")
    print("\nNext steps:")
    print("1. Review generated files in evaluation/data/")
    print("2. Delete or edit any examples you don't want")
    print("3. Run: uv run python -m evaluation.fund_search_eval_dataset")
    print("4. Run evaluation: MLFLOW_ENABLED=true uv run python -m evaluation.evaluate")


if __name__ == "__main__":
    main()
