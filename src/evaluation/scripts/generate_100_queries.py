import json

# Define the 100 queries structure
# Tier 1: Basic (Direct criteria, single intent) - 40 queries
# Tier 2: Intermediate (Dual criteria, comparisons, rankings) - 40 queries
# Tier 3: Advanced (Ambiguous, complex constraints, semantic nuances) - 20 queries

queries = []

# --- Tier 1: Basic (40) ---
basic_templates = [
    # Company/Provider Search (10)
    ("Show me funds from Itau", {"service_provider_entity": ["Itau"]}, "provider_search"),
    ("Funds managed by Bradesco", {"service_provider_entity": ["Bradesco"]}, "provider_search"),
    ("List BTG Pactual funds", {"service_provider_entity": ["BTG Pactual"]}, "provider_search"),
    ("XP Asset Management funds", {"service_provider_entity": ["XP Asset Management"]}, "provider_search"),
    ("Funds from Vinci Partners", {"service_provider_entity": ["Vinci Partners"]}, "provider_search"),
    ("Safra funds", {"service_provider_entity": ["Safra"]}, "provider_search"),
    ("Kinea funds", {"service_provider_entity": ["Kinea"]}, "provider_search"),
    ("Opportunity funds", {"service_provider_entity": ["Opportunity"]}, "provider_search"),
    ("Funds by Santander", {"service_provider_entity": ["Santander"]}, "provider_search"),
    ("Verde Asset funds", {"service_provider_entity": ["Verde Asset"]}, "provider_search"),

    # Asset Class (10)
    ("Find equity funds", {"investment_class": "Ações"}, "class_search"),
    ("I want fixed income funds", {"investment_class": "Renda Fixa"}, "class_search"),
    ("Multimarket funds", {"investment_class": "Multimercado"}, "class_search"),
    ("Foreign debt funds", {"investment_class": "Dívida Externa"}, "class_search"),
    ("FIP funds", {"fund_type": ["FIP"]}, "type_search"),
    ("FII funds", {"fund_type": ["FII"]}, "type_search"),
    ("ETF funds", {"fund_type": ["ETF"]}, "type_search"),
    ("Referenciado funds", {"investment_class": "Referenciado"}, "class_search"),
    ("Cambial funds", {"investment_class": "Cambial"}, "class_search"),
    ("Short term funds", {"investment_class": "Curto Prazo"}, "class_search"),

    # Audience (5)
    ("Funds for professional investors", {"target_audience": ["PROFESSIONAL"]}, "audience_search"),
    ("Funds for qualified investors", {"target_audience": ["QUALIFIED"]}, "audience_search"),
    ("Retail funds", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("Funds for general public", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("Restricted funds for professionals", {"target_audience": ["PROFESSIONAL"]}, "audience_search"),

    # Simple Holdings (5)
    ("Funds holding Petrobras", {"asset_name": ["Petrobras"], "asset_tickers": ["PETR3", "PETR4"]}, "holdings_search"),
    ("Funds with Vale shares", {"asset_name": ["Vale"], "asset_tickers": ["VALE3"]}, "holdings_search"),
    ("Funds invested in Itaú", {"asset_name": ["Itaú"], "asset_tickers": ["ITUB4"]}, "holdings_search"),
    ("Exposure to Banco do Brasil", {"asset_name": ["Banco do Brasil"], "asset_tickers": ["BBAS3"]}, "holdings_search"),
    ("Funds with Ambev", {"asset_name": ["Ambev"], "asset_tickers": ["ABEV3"]}, "holdings_search"),

    # Simple Names (5)
    ("Find Alaska Black", {"fund_legal_name": "Alaska Black"}, "name_search"),
    ("Search for Verde Scena", {"fund_legal_name": "Verde Scena"}, "name_search"),
    ("Dynamo Cougar fund", {"fund_legal_name": "Dynamo Cougar"}, "name_search"),
    ("Kapitalo Kappa", {"fund_legal_name": "Kapitalo Kappa"}, "name_search"),
    ("SPX Nimitz", {"fund_legal_name": "SPX Nimitz"}, "name_search"),

    # Misc Basic (5)
    ("Show me everything", {}, "browse_general"),
    ("List all funds", {}, "browse_general"),
    ("Exclusive funds", {"is_exclusive_fund": True}, "boolean_search"),
    ("Non-exclusive funds", {"is_exclusive_fund": False}, "boolean_search"),
    ("Funds that can invest abroad", {"can_invest_abroad_100_pct": True}, "boolean_search"),
]

for q, crit, cat in basic_templates:
    queries.append({
        "query": q,
        "expected_criteria": crit,
        "description": f"Basic {cat}",
        "category": cat,
        "tier": "basic",
        "validation_type": "criteria_match"
    })

# --- Tier 2: Intermediate (40) ---
intermediate_templates = [
    # Dual Criteria (10)
    ("Equity funds from Itau", {"investment_class": "Ações", "service_provider_entity": ["Itau"]}, "dual_criteria"),
    ("Fixed income funds for qualified investors", {"investment_class": "Renda Fixa", "target_audience": ["QUALIFIED"]}, "dual_criteria"),
    ("Multimarket funds managed by Verde", {"investment_class": "Multimercado", "service_provider_entity": ["Verde"]}, "dual_criteria"),
    ("FIP funds for professionals", {"fund_type": ["FIP"], "target_audience": ["PROFESSIONAL"]}, "dual_criteria"),
    ("Exclusive equity funds", {"investment_class": "Ações", "is_exclusive_fund": True}, "dual_criteria"),
    ("Retail cambial funds", {"investment_class": "Cambial", "target_audience": ["RETAIL"]}, "dual_criteria"),
    ("FIIs managed by Kinea", {"fund_type": ["FII"], "service_provider_entity": ["Kinea"]}, "dual_criteria"),
    ("Long term tax funds from Bradesco", {"has_long_term_taxation": True, "service_provider_entity": ["Bradesco"]}, "dual_criteria"),
    ("Foreign debt funds for retail", {"investment_class": "Dívida Externa", "target_audience": ["RETAIL"]}, "dual_criteria"),
    ("Non-exclusive multimarket funds", {"investment_class": "Multimercado", "is_exclusive_fund": False}, "dual_criteria"),

    # Rankings (10)
    ("Top 10 equity funds", {"investment_class": "Ações", "numeric_filter": {"metric": "return", "operator": "top", "top_n": 10}}, "ranking"),
    ("Best performing fixed income funds", {"investment_class": "Renda Fixa", "numeric_filter": {"metric": "return", "operator": "top"}}, "ranking"),
    ("Highest return funds from XP", {"service_provider_entity": ["XP"], "numeric_filter": {"metric": "return", "operator": "max"}}, "ranking"),
    ("Funds with lowest admin fee", {"numeric_filter": {"metric": "management_fee", "operator": "min"}}, "ranking"),
    ("Largest funds by AUM", {"numeric_filter": {"metric": "aum", "operator": "max"}}, "ranking"),
    ("Top 5 FIIs", {"fund_type": ["FII"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 5}}, "ranking"),
    ("Best multimarket funds last 12 months", {"investment_class": "Multimercado", "numeric_filter": {"metric": "return", "operator": "top", "performance_period": "12m"}}, "ranking"),
    ("Top 3 funds holding Vale", {"asset_name": ["Vale"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 3}}, "ranking"),
    ("Worst performing funds", {"numeric_filter": {"metric": "return", "operator": "min"}}, "ranking"), # Ambiguous min vs worst
    ("Most popular funds", {"numeric_filter": {"metric": "holders", "operator": "max"}}, "ranking"),

    # Numeric Filters (10)
    ("Funds with min investment 1000", {"numeric_filter": {"metric": "min_investment", "operator": "min", "value": 1000}}, "numeric_filter"), # Note: min_investment not in schema yet, likely will fail/be generic
    ("Funds with admin fee less than 1%", {"numeric_filter": {"metric": "management_fee", "operator": "max", "value": 1.0}}, "numeric_filter"),
    ("Funds with return above CDI", {"numeric_filter": {"metric": "return", "operator": "min", "benchmark_name": "CDI"}}, "numeric_filter"),
    ("Funds beating Ibovespa", {"numeric_filter": {"metric": "return", "operator": "min", "benchmark_name": "IBOVESPA"}}, "numeric_filter"),
    ("Funds with more than 10k investors", {"numeric_filter": {"metric": "holders", "operator": "min", "value": 10000}}, "numeric_filter"),
    ("Funds with AUM over 1 billion", {"numeric_filter": {"metric": "aum", "operator": "min", "value": 1000000000}}, "numeric_filter"),
    ("Funds with performance fee", {"numeric_filter": {"metric": "performance_fee", "operator": "min", "value": 0}}, "numeric_filter"), # Implied existence
    ("Funds charging 2% admin fee", {"numeric_filter": {"metric": "management_fee", "operator": "around", "value": 2.0}}, "numeric_filter"),
    ("Funds yielding 10% this year", {"numeric_filter": {"metric": "return", "operator": "around", "value": 10, "performance_period": "ytd"}}, "numeric_filter"),
    ("Cheap funds", {"numeric_filter": {"metric": "management_fee", "operator": "min"}}, "numeric_filter"), # Qualitative

    # Semantic/Strategy (10)
    ("Crypto funds", {"semantic_query": "crypto bitcoin blockchain"}, "thematic"),
    ("ESG funds", {"semantic_query": "ESG sustainable green"}, "thematic"),
    ("Tech funds", {"semantic_query": "technology tech nasdaq"}, "thematic"),
    ("Gold funds", {"semantic_query": "gold ouro"}, "thematic"),
    ("Cannabis funds", {"semantic_query": "cannabis marijuana"}, "thematic"),
    ("Infrastructure funds", {"semantic_query": "infrastructure infraestrutura debentures"}, "thematic"),
    ("Small cap funds", {"semantic_query": "small caps"}, "thematic"),
    ("Dividend funds", {"semantic_query": "dividends dividendos income"}, "thematic"),
    ("Real estate paper funds", {"semantic_query": "papel recebiveis cri"}, "thematic"),
    ("Agro funds", {"semantic_query": "agro agronegocio fiagro"}, "thematic"),
]

for q, crit, cat in intermediate_templates:
    queries.append({
        "query": q,
        "expected_criteria": crit,
        "description": f"Intermediate {cat}",
        "category": cat,
        "tier": "intermediate",
        "validation_type": "criteria_match"
    })

# --- Tier 3: Advanced/Tricky (20) ---
advanced_templates = [
    # Ambiguous Names vs Types
    ("I want funds dealing with Dolar", {"fund_legal_name": "Dolar", "investment_class": "Cambial"}, "ambiguous_name_type"), # Could be name or class
    ("Give me Verde funds", {"service_provider_entity": ["Verde"], "fund_legal_name": "Verde"}, "ambiguous_provider_name"), # Provider 'Verde Asset' or name 'Verde'
    ("Funds named Strategy", {"fund_legal_name": "Strategy"}, "tricky_name"), # 'Strategy' is a generic word

    # Complex Boolean Logic
    ("Non-exclusive equity funds for retail", {"is_exclusive_fund": False, "investment_class": "Ações", "target_audience": ["RETAIL"]}, "complex_boolean"),
    ("FIPs not for pros", {"fund_type": ["FIP"], "target_audience": ["QUALIFIED", "RETAIL"]}, "complex_negation"), # Implied negation of professional

    # Multi-step / Conversational (simulated as one-shot here)
    ("I have 1 million to invest in aggressive funds", {"numeric_filter": {"metric": "min_investment", "operator": "max", "value": 1000000}, "semantic_query": "aggressive aggressive_growth"}, "contextual"),
    ("Safe funds for my grandmother", {"semantic_query": "conservative conservador renda fixa low_risk"}, "contextual_risk"),
    
    # Specific Regulations/Niche
    ("Funds 175", {"semantic_query": "cvm 175"}, "regulatory"), # CVM 175 rule
    ("Incentivized debenture funds", {"semantic_query": "debentures incentivadas", "investment_class": "Renda Fixa"}, "niche_product"),
    
    # Holdings Cross-Reference
    ("Funds holding Tesla and Apple", {"asset_name": ["Tesla", "Apple"], "asset_tickers": ["TSLA34", "AAPL34"]}, "multi_holding"),
    
    # Provider Roles
    ("Funds administered by BTG but managed by someone else", {"service_provider_entity": ["BTG Pactual"]}, "role_specific"), # Hard to capture 'managed by someone else' in current schema
    
    # Tricky Negations
    ("Funds that are NOT multimarket", {"investment_class": None}, "negation"), # Schema doesn't support NOT yet, expected is None or semantic handle?
    
    # Fuzzy Dates
    ("Funds launched last year", {"semantic_query": "new funds recent launch"}, "temporal"),
    
    # Mixed Language
    ("Fundos de equity com low fees", {"investment_class": "Ações", "numeric_filter": {"metric": "management_fee", "operator": "min"}}, "mixed_lang"),
    
    # Typos
    ("Eqity fnds from Itau", {"investment_class": "Ações", "service_provider_entity": ["Itau"]}, "typo_correction"),
    ("Bradsco funds", {"service_provider_entity": ["Bradesco"]}, "typo_correction"),
    
    # Very Specific
    ("Funds tracking the IMA-B 5", {"semantic_query": "IMA-B 5", "numeric_filter": {"benchmark_name": "IMA-B 5"}}, "specific_benchmark"),
    
    # Conversational Fluff
    ("Hey bot, can you please find me some nice tech funds?", {"semantic_query": "technology tech"}, "conversational"),
    ("I am looking for a fund that invests in startups", {"fund_type": ["FIP"], "semantic_query": "venture capital startups"}, "inference"),
]

for q, crit, cat in advanced_templates:
    queries.append({
        "query": q,
        "expected_criteria": crit,
        "description": f"Advanced {cat}",
        "category": cat,
        "tier": "advanced",
        "validation_type": "criteria_match"
    })

# Write to JSONL
with open("src/evaluation/data/proposed_queries_100.jsonl", "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

print(f"Generated {len(queries)} queries.")

