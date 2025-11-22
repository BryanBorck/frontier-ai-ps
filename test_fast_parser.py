import sys
from src.tools.tool_parse_query.fast_parser import fast_parse

def test_query(query):
    result = fast_parse(query)
    print(f"Query: '{query}'")
    if result:
        print(f"  Fund Legal Name: {result.fund_legal_name}")
        print(f"  Service Provider: {result.service_provider_entity}")
    else:
        print("  No match (fallback to LLM)")
    print("-" * 20)

queries = [
    "fundos itau",
    "investimentos btg",
    "banco do brasil renda fixa",
    "bny mellon funds",
    "credit suisse fii",
    "jpmorgan multimercado",
    "orama acoes",
    "votorantim credito privado",
    "fundos clear", # Should miss if I didn't add clear
    "fundo xp",
]

for q in queries:
    test_query(q)

