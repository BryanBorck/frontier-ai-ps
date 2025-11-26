import json

# Define 200 queries structure
# Tier 1: Basic (60 queries) - Direct criteria, simple names
# Tier 2: Intermediate (60 queries) - Dual criteria, rankings, numeric
# Tier 3: Advanced (40 queries) - Ambiguous, edge cases, context
# Tier 4: Edge Cases / Conversational (40 queries) - Vague, off-topic, follow-ups

queries = []

# --- Tier 1: Basic (60) ---
basic_templates = [
    # Provider (15)
    ("Funds from Itau", {"service_provider_entity": ["Itau"]}, "provider_search"),
    ("Bradesco funds", {"service_provider_entity": ["Bradesco"]}, "provider_search"),
    ("Santander funds", {"service_provider_entity": ["Santander"]}, "provider_search"),
    ("BTG Pactual funds", {"service_provider_entity": ["BTG Pactual"]}, "provider_search"),
    ("XP funds", {"service_provider_entity": ["XP Asset Management"]}, "provider_search"),
    ("Vinci Partners funds", {"service_provider_entity": ["Vinci Partners"]}, "provider_search"),
    ("Safra funds", {"service_provider_entity": ["Safra"]}, "provider_search"),
    ("Kinea funds", {"service_provider_entity": ["Kinea"]}, "provider_search"),
    ("Opportunity funds", {"service_provider_entity": ["Opportunity"]}, "provider_search"),
    ("Verde Asset funds", {"service_provider_entity": ["Verde Asset"]}, "provider_search"),
    ("Nubank funds", {"service_provider_entity": ["Nu Asset Management"]}, "provider_search"), # Nu Asset
    ("Banco do Brasil funds", {"service_provider_entity": ["BB Asset"]}, "provider_search"),
    ("Caixa funds", {"service_provider_entity": ["Caixa Asset"]}, "provider_search"),
    ("Credit Suisse funds", {"service_provider_entity": ["Credit Suisse"]}, "provider_search"),
    ("JGP funds", {"service_provider_entity": ["JGP"]}, "provider_search"),

    # Asset Class (15)
    ("Equity funds", {"investment_class": "Ações"}, "class_search"),
    ("Fixed Income funds", {"investment_class": "Renda Fixa"}, "class_search"),
    ("Multimarket funds", {"investment_class": "Multimercado"}, "class_search"),
    ("Foreign Debt funds", {"investment_class": "Dívida Externa"}, "class_search"),
    ("Cambial funds", {"investment_class": "Cambial"}, "class_search"),
    ("Short Term funds", {"investment_class": "Curto Prazo"}, "class_search"),
    ("Referenciado funds", {"investment_class": "Referenciado"}, "class_search"),
    ("FIP funds", {"fund_type": ["FIP"]}, "type_search"),
    ("FII funds", {"fund_type": ["FII"]}, "type_search"),
    ("ETF funds", {"fund_type": ["ETF"]}, "type_search"),
    ("FIDC funds", {"fund_type": ["FIDC"]}, "type_search"),
    ("FITVM funds", {"fund_type": ["FITVM"]}, "type_search"),
    ("Infrastructure debenture funds", {"semantic_query": "debentures incentivadas infraestrutura"}, "class_search"), # Semantic fallback
    ("Real estate funds", {"fund_type": ["FII"]}, "type_search"),
    ("Pension funds", {"semantic_query": "previdencia previdenciario"}, "class_search"),

    # Audience (10)
    ("Funds for professional investors", {"target_audience": ["PROFESSIONAL"]}, "audience_search"),
    ("Funds for qualified investors", {"target_audience": ["QUALIFIED"]}, "audience_search"),
    ("Retail funds", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("General public funds", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("Institutional funds", {"target_audience": ["PROFESSIONAL"]}, "audience_search"), # Mapping logic needed
    ("Funds for beginners", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("Private bank funds", {"semantic_query": "private high net worth"}, "audience_search"), # Semantic
    ("Exclusive funds", {"is_exclusive_fund": True}, "boolean_search"),
    ("Non-exclusive funds", {"is_exclusive_fund": False}, "boolean_search"),
    ("Open funds", {"semantic_query": "aberto captacao"}, "boolean_search"),

    # Holdings (10)
    ("Funds holding Petrobras", {"asset_name": ["Petrobras"], "asset_tickers": ["PETR3", "PETR4"]}, "holdings_search"),
    ("Funds with Vale", {"asset_name": ["Vale"], "asset_tickers": ["VALE3"]}, "holdings_search"),
    ("Funds invested in Itau", {"asset_name": ["Itaú"], "asset_tickers": ["ITUB4"]}, "holdings_search"),
    ("Funds with Ambev", {"asset_name": ["Ambev"], "asset_tickers": ["ABEV3"]}, "holdings_search"),
    ("Exposure to Banco do Brasil", {"asset_name": ["Banco do Brasil"], "asset_tickers": ["BBAS3"]}, "holdings_search"),
    ("Funds holding WEG", {"asset_name": ["WEG"], "asset_tickers": ["WEGE3"]}, "holdings_search"),
    ("Funds with Magalu", {"asset_name": ["Magazine Luiza"], "asset_tickers": ["MGLU3"]}, "holdings_search"),
    ("Funds with Tesla", {"asset_name": ["Tesla"], "asset_tickers": ["TSLA34"]}, "holdings_search"),
    ("Funds with Apple", {"asset_name": ["Apple"], "asset_tickers": ["AAPL34"]}, "holdings_search"),
    ("Funds with Nubank", {"asset_name": ["Nubank"], "asset_tickers": ["ROXO34"]}, "holdings_search"),

    # Names (10)
    ("Alaska Black", {"fund_legal_name": "Alaska Black"}, "name_search"),
    ("Verde Scena", {"fund_legal_name": "Verde Scena"}, "name_search"),
    ("Dynamo Cougar", {"fund_legal_name": "Dynamo Cougar"}, "name_search"),
    ("SPX Nimitz", {"fund_legal_name": "SPX Nimitz"}, "name_search"),
    ("Kapitalo Kappa", {"fund_legal_name": "Kapitalo Kappa"}, "name_search"),
    ("Occam Retorno Absoluto", {"fund_legal_name": "Occam Retorno Absoluto"}, "name_search"),
    ("Ibiuna Hedge", {"fund_legal_name": "Ibiuna Hedge"}, "name_search"),
    ("Legacy Capital", {"fund_legal_name": "Legacy Capital"}, "name_search"),
    ("Absoluto Partners", {"fund_legal_name": "Absoluto Partners"}, "name_search"),
    ("Constellation", {"fund_legal_name": "Constellation"}, "name_search"),
]

for q, crit, cat in basic_templates:
    queries.append({
        "query": q,
        "expected_criteria": crit,
        "expected_response_type": "list_results" if "fund_legal_name" not in crit else "single_match",
        "description": f"Basic {cat}",
        "category": cat,
        "tier": "basic",
        "validation_type": "criteria_match"
    })

# --- Tier 2: Intermediate (60) ---
intermediate_templates = [
    # Dual Criteria (20)
    ("Equity funds Itau", {"investment_class": "Ações", "service_provider_entity": ["Itau"]}, "dual_criteria"),
    ("Fixed Income Qualified", {"investment_class": "Renda Fixa", "target_audience": ["QUALIFIED"]}, "dual_criteria"),
    ("Multimarket Verde", {"investment_class": "Multimercado", "service_provider_entity": ["Verde"]}, "dual_criteria"),
    ("FIP Professional", {"fund_type": ["FIP"], "target_audience": ["PROFESSIONAL"]}, "dual_criteria"),
    ("Exclusive Equity", {"investment_class": "Ações", "is_exclusive_fund": True}, "dual_criteria"),
    ("Retail Cambial", {"investment_class": "Cambial", "target_audience": ["RETAIL"]}, "dual_criteria"),
    ("FII Kinea", {"fund_type": ["FII"], "service_provider_entity": ["Kinea"]}, "dual_criteria"),
    ("Long Term Tax Bradesco", {"has_long_term_taxation": True, "service_provider_entity": ["Bradesco"]}, "dual_criteria"),
    ("Foreign Debt Retail", {"investment_class": "Dívida Externa", "target_audience": ["RETAIL"]}, "dual_criteria"),
    ("Non-exclusive Multimarket", {"investment_class": "Multimercado", "is_exclusive_fund": False}, "dual_criteria"),
    ("Ibiuna Fixed Income", {"service_provider_entity": ["Ibiuna"], "investment_class": "Renda Fixa"}, "dual_criteria"),
    ("SPX Multimarket", {"service_provider_entity": ["SPX"], "investment_class": "Multimercado"}, "dual_criteria"),
    ("Credit Suisse Equity", {"service_provider_entity": ["Credit Suisse"], "investment_class": "Ações"}, "dual_criteria"),
    ("BTG Pactual FII", {"service_provider_entity": ["BTG Pactual"], "fund_type": ["FII"]}, "dual_criteria"),
    ("Vinci Partners FIP", {"service_provider_entity": ["Vinci Partners"], "fund_type": ["FIP"]}, "dual_criteria"),
    ("Safra Retail", {"service_provider_entity": ["Safra"], "target_audience": ["RETAIL"]}, "dual_criteria"),
    ("Opportunity Qualified", {"service_provider_entity": ["Opportunity"], "target_audience": ["QUALIFIED"]}, "dual_criteria"),
    ("XP Exclusive", {"service_provider_entity": ["XP"], "is_exclusive_fund": True}, "dual_criteria"),
    ("BB Asset Multimarket", {"service_provider_entity": ["BB Asset"], "investment_class": "Multimercado"}, "dual_criteria"),
    ("Caixa Fixed Income", {"service_provider_entity": ["Caixa Asset"], "investment_class": "Renda Fixa"}, "dual_criteria"),

    # Ranking (20)
    ("Top 10 equity funds", {"investment_class": "Ações", "numeric_filter": {"metric": "return", "operator": "top", "top_n": 10}}, "ranking"),
    ("Best fixed income", {"investment_class": "Renda Fixa", "numeric_filter": {"metric": "return", "operator": "top"}}, "ranking"),
    ("Highest return XP", {"service_provider_entity": ["XP"], "numeric_filter": {"metric": "return", "operator": "max"}}, "ranking"),
    ("Lowest fee funds", {"numeric_filter": {"metric": "management_fee", "operator": "min"}}, "ranking"),
    ("Largest funds AUM", {"numeric_filter": {"metric": "aum", "operator": "max"}}, "ranking"),
    ("Top 5 FIIs", {"fund_type": ["FII"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 5}}, "ranking"),
    ("Best multimarket 12m", {"investment_class": "Multimercado", "numeric_filter": {"metric": "return", "operator": "top", "performance_period": "12m"}}, "ranking"),
    ("Top 3 holding Vale", {"asset_name": ["Vale"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 3}}, "ranking"),
    ("Worst performing funds", {"numeric_filter": {"metric": "return", "operator": "min"}}, "ranking"),
    ("Most popular funds", {"numeric_filter": {"metric": "holders", "operator": "max"}}, "ranking"),
    ("Top 10 Itau funds", {"service_provider_entity": ["Itau"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 10}}, "ranking"),
    ("Best funds 2024", {"numeric_filter": {"metric": "return", "operator": "top", "performance_period": "ytd"}}, "ranking"),
    ("Highest yield FIIs", {"fund_type": ["FII"], "numeric_filter": {"metric": "return", "operator": "top"}}, "ranking"), # Yield ~ Return
    ("Lowest volatility funds", {"semantic_query": "low volatility", "numeric_filter": {"metric": "return", "operator": "min"}}, "ranking"), # Volatility metric missing, proxy?
    ("Top performing small caps", {"semantic_query": "small caps", "numeric_filter": {"metric": "return", "operator": "top"}}, "ranking"),
    ("Best ESG funds", {"semantic_query": "ESG", "numeric_filter": {"metric": "return", "operator": "top"}}, "ranking"),
    ("Cheapest equity funds", {"investment_class": "Ações", "numeric_filter": {"metric": "management_fee", "operator": "min"}}, "ranking"),
    ("Top 5 funds beating CDI", {"numeric_filter": {"metric": "return", "operator": "top", "top_n": 5, "benchmark_name": "CDI"}}, "ranking"),
    ("Best funds last 3 years", {"numeric_filter": {"metric": "return", "operator": "top", "performance_period": "36m"}}, "ranking"),
    ("Top funds holding Petrobras", {"asset_name": ["Petrobras"], "numeric_filter": {"metric": "return", "operator": "top"}}, "ranking"),

    # Numeric (10)
    ("Min investment 1000", {"numeric_filter": {"metric": "min_investment", "operator": "min", "value": 1000}}, "numeric"),
    ("Admin fee < 1%", {"numeric_filter": {"metric": "management_fee", "operator": "max", "value": 1.0}}, "numeric"),
    ("Return > CDI", {"numeric_filter": {"metric": "return", "operator": "min", "benchmark_name": "CDI"}}, "numeric"),
    ("Beat Ibovespa", {"numeric_filter": {"metric": "return", "operator": "min", "benchmark_name": "IBOVESPA"}}, "numeric"),
    ("> 10k investors", {"numeric_filter": {"metric": "holders", "operator": "min", "value": 10000}}, "numeric"),
    ("AUM > 1 billion", {"numeric_filter": {"metric": "aum", "operator": "min", "value": 1000000000}}, "numeric"),
    ("Has performance fee", {"numeric_filter": {"metric": "performance_fee", "operator": "min", "value": 0}}, "numeric"),
    ("Fee around 2%", {"numeric_filter": {"metric": "management_fee", "operator": "around", "value": 2.0}}, "numeric"),
    ("Yield 10% YTD", {"numeric_filter": {"metric": "return", "operator": "around", "value": 10, "performance_period": "ytd"}}, "numeric"),
    ("Zero admin fee", {"numeric_filter": {"metric": "management_fee", "operator": "exact", "value": 0}}, "numeric"),

    # Thematic (10)
    ("Crypto funds", {"semantic_query": "crypto bitcoin blockchain"}, "thematic"),
    ("ESG funds", {"semantic_query": "ESG sustainable green"}, "thematic"),
    ("Tech funds", {"semantic_query": "technology tech nasdaq"}, "thematic"),
    ("Gold funds", {"semantic_query": "gold ouro"}, "thematic"),
    ("Cannabis funds", {"semantic_query": "cannabis marijuana"}, "thematic"),
    ("Infrastructure funds", {"semantic_query": "infrastructure infraestrutura debentures"}, "thematic"),
    ("Small cap funds", {"semantic_query": "small caps"}, "thematic"),
    ("Dividend funds", {"semantic_query": "dividends dividendos income"}, "thematic"),
    ("Real estate paper", {"semantic_query": "papel recebiveis cri"}, "thematic"),
    ("Agro funds", {"semantic_query": "agro agronegocio fiagro"}, "thematic"),
]

for q, crit, cat in intermediate_templates:
    queries.append({
        "query": q,
        "expected_criteria": crit,
        "expected_response_type": "list_results" if "top" not in str(crit) else "list_results", # Rankings are lists
        "description": f"Intermediate {cat}",
        "category": cat,
        "tier": "intermediate",
        "validation_type": "criteria_match"
    })

# --- Tier 3: Advanced (40) ---
advanced_templates = [
    # Ambiguous (10)
    ("Funds dealing with Dolar", {"fund_legal_name": "Dolar", "investment_class": "Cambial"}, "ambiguous_name_type"),
    ("Give me Verde funds", {"service_provider_entity": ["Verde"], "fund_legal_name": "Verde"}, "ambiguous_provider_name"),
    ("Funds named Strategy", {"fund_legal_name": "Strategy"}, "tricky_name"),
    ("Funds focusing on Credit", {"investment_class": "Renda Fixa", "semantic_query": "credito privado"}, "ambiguous_class"),
    ("Real Estate funds", {"fund_type": ["FII"], "semantic_query": "imobiliario"}, "ambiguous_type"),
    ("Funds investing in Gold", {"semantic_query": "gold ouro", "investment_class": "Multimercado"}, "ambiguous_asset"), # Often Multimercado
    ("Funds for kids", {"target_audience": ["RETAIL"], "semantic_query": "menores idade"}, "ambiguous_audience"),
    ("Safe funds", {"investment_class": "Renda Fixa", "semantic_query": "safe conservador"}, "ambiguous_risk"),
    ("Aggressive funds", {"investment_class": "Ações", "semantic_query": "aggressive agressivo"}, "ambiguous_risk"),
    ("Global funds", {"investment_class": "Dívida Externa", "semantic_query": "global internacional"}, "ambiguous_class"),

    # Complex Logic (10)
    ("Non-exclusive equity retail", {"is_exclusive_fund": False, "investment_class": "Ações", "target_audience": ["RETAIL"]}, "complex_boolean"),
    ("FIPs not for pros", {"fund_type": ["FIP"], "target_audience": ["QUALIFIED", "RETAIL"]}, "complex_negation"),
    ("Itau funds but not multimarket", {"service_provider_entity": ["Itau"], "investment_class": None}, "negation"), # Schema fail
    ("Funds holding Vale AND Petrobras", {"asset_name": ["Vale", "Petrobras"]}, "multi_holding"),
    ("Equity funds OR Fixed Income", {"investment_class": ["Ações", "Renda Fixa"]}, "multi_class"), # Schema fail? List supported?
    ("Top 5 funds excl. Itau", {"numeric_filter": {"metric": "return", "operator": "top", "top_n": 5}}, "negation_provider"),
    ("Funds with fee < 1% AND > 1B AUM", {"numeric_filter": {"metric": "aum", "operator": "min"}}, "multi_numeric"), # Only 1 numeric filter supported usually
    ("Exclusive funds from Bradesco or Itau", {"is_exclusive_fund": True, "service_provider_entity": ["Bradesco", "Itau"]}, "multi_provider"),
    ("Funds holding tech stocks", {"semantic_query": "tech stocks", "asset_type": ["EQUITY"]}, "semantic_holding"),
    ("Funds launched recently", {"semantic_query": "recent launch novo"}, "temporal"),

    # Edge Cases (10)
    ("Funds 175", {"semantic_query": "cvm 175"}, "regulatory"),
    ("Incentivized debentures", {"semantic_query": "debentures incentivadas", "investment_class": "Renda Fixa"}, "niche"),
    ("Fiagro", {"fund_type": ["FIAGRO"], "semantic_query": "fiagro"}, "niche"), # FIAGRO type missing in schema
    ("Funds with liquidity D+0", {"semantic_query": "liquidez diaria d+0"}, "liquidity"),
    ("Funds with exit fee", {"numeric_filter": {"metric": "exit_fee", "operator": "min", "value": 0}}, "fee_type"), # exit_fee missing
    ("Master funds", {"semantic_query": "master"}, "structure"),
    ("Feeder funds", {"semantic_query": "feeder fic"}, "structure"),
    ("Restricted funds", {"is_exclusive_fund": True}, "access"),
    ("Funds for non-residents", {"semantic_query": "investidor nao residente"}, "audience"),
    ("Funds with currency hedge", {"semantic_query": "hedge cambial"}, "strategy"),

    # Tricky Syntax (10)
    ("Fundos de equity low fees", {"investment_class": "Ações", "numeric_filter": {"metric": "management_fee", "operator": "min"}}, "mixed_lang"),
    ("Eqity fnds Itau", {"investment_class": "Ações", "service_provider_entity": ["Itau"]}, "typo"),
    ("Bradsco funds", {"service_provider_entity": ["Bradesco"]}, "typo"),
    ("FDS from XP", {"service_provider_entity": ["XP"]}, "abbr"),
    ("MM funds", {"investment_class": "Multimercado"}, "abbr"),
    ("RF funds", {"investment_class": "Renda Fixa"}, "abbr"),
    ("FIA funds", {"fund_type": ["FIA"], "investment_class": "Ações"}, "abbr"), # FIA = Fundo Investimento Ações
    ("FIM funds", {"fund_type": ["FIM"], "investment_class": "Multimercado"}, "abbr"), # FIM = Fundo Investimento Multimercado
    ("FIRF funds", {"fund_type": ["FIRF"], "investment_class": "Renda Fixa"}, "abbr"),
    ("Funds w/ high rtn", {"numeric_filter": {"metric": "return", "operator": "max"}}, "abbr"),
]

for q, crit, cat in advanced_templates:
    queries.append({
        "query": q,
        "expected_criteria": crit,
        "expected_response_type": "list_results", # Usually list unless specific ambiguity logic triggers followup
        "description": f"Advanced {cat}",
        "category": cat,
        "tier": "advanced",
        "validation_type": "criteria_match"
    })

# --- Tier 4: Edge / Vague / Conversational (40) ---
vague_templates = [
    # Too Vague (10)
    ("Funds", {}, "too_vague"),
    ("Invest", {}, "too_vague"),
    ("Money", {}, "too_vague"),
    ("Help me", {}, "too_vague"),
    ("I want to invest", {}, "too_vague"),
    ("Show funds", {}, "too_vague"),
    ("Best funds", {}, "too_vague"), # Arguably vague without criteria
    ("Good funds", {}, "too_vague"),
    ("List all", {}, "too_vague"), # "too_many_results"
    ("Search", {}, "too_vague"),

    # Conversational (10)
    ("Hello", {}, "greeting"),
    ("Hi", {}, "greeting"),
    ("Good morning", {}, "greeting"),
    ("Who are you?", {}, "identity"),
    ("What can you do?", {}, "capabilities"),
    ("Thanks", {}, "closing"),
    ("Bye", {}, "closing"),
    ("Cool", {}, "feedback"),
    ("Okay", {}, "ack"),
    ("Explain FII", {}, "informational"),

    # Off-topic (10)
    ("Weather in Sao Paulo", {}, "off_topic"),
    ("Recipe for cake", {}, "off_topic"),
    ("Who is the president?", {}, "off_topic"),
    ("Buy bitcoin", {}, "off_topic"), # Maybe crypto fund?
    ("Stock price PETR4", {}, "market_data"), # Not fund search
    ("Dollar rate", {}, "market_data"),
    ("Selic rate today", {}, "market_data"),
    ("Inflation Brazil", {}, "market_data"),
    ("GDP Brazil", {}, "market_data"),
    ("Sports news", {}, "off_topic"),

    # Follow-ups (10)
    ("More", {}, "followup"),
    ("Next 10", {}, "followup"),
    ("Cheaper ones", {}, "followup_refine"),
    ("Better returns", {}, "followup_refine"),
    ("Only Itau", {}, "followup_refine"),
    ("Remove FIP", {}, "followup_refine"),
    ("Add Bradesco", {}, "followup_refine"),
    ("What about Vale?", {}, "followup_refine"),
    ("Show details", {}, "followup_action"),
    ("Compare them", {}, "followup_action"),
]

for q, crit, cat in vague_templates:
    # Logic for expected response type based on category
    if cat == "too_vague":
        rtype = "followup" # Should ask clarification
    elif cat in ["greeting", "identity", "capabilities", "closing", "feedback", "ack"]:
        rtype = "informational" # Or chat
    elif cat == "off_topic":
        rtype = "no_results" # Or off_topic handler
    elif cat == "informational":
        rtype = "informational"
    elif "followup" in cat:
        rtype = "list_results" # Assumes context exists? Hard to eval stateless.
        # For stateless evaluation, these are tricky. We'll label as 'followup' intent usually.
    else:
        rtype = "no_results"

    queries.append({
        "query": q,
        "expected_criteria": crit,
        "expected_response_type": rtype,
        "description": f"Vague/Edge {cat}",
        "category": cat,
        "tier": "edge_case",
        "validation_type": "response_type_match"
    })

# Write to JSONL
with open("src/evaluation/data/proposed_queries_200.jsonl", "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

print(f"Generated {len(queries)} queries.")

