import json

# Define 250 queries structure
# Tier 1: Basic (60 queries) - Direct criteria, simple names
# Tier 2: Intermediate (60 queries) - Dual criteria, rankings, numeric
# Tier 3: Advanced (50 queries) - Ambiguous, edge cases, context, semantic strategy
# Tier 4: Edge / Vague / Conversational / Error (80 queries) - Vague, off-topic, follow-ups, misspellings

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
    ("Infrastructure debenture funds", {"semantic_query": "debentures incentivadas infraestrutura"}, "class_search"),
    ("Real estate funds", {"fund_type": ["FII"]}, "type_search"),
    ("Pension funds", {"semantic_query": "previdencia previdenciario"}, "class_search"),

    # Audience (10)
    ("Funds for professional investors", {"target_audience": ["PROFESSIONAL"]}, "audience_search"),
    ("Funds for qualified investors", {"target_audience": ["QUALIFIED"]}, "audience_search"),
    ("Retail funds", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("General public funds", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("Institutional funds", {"target_audience": ["PROFESSIONAL"]}, "audience_search"),
    ("Funds for beginners", {"target_audience": ["RETAIL"]}, "audience_search"),
    ("Private bank funds", {"semantic_query": "private high net worth"}, "audience_search"),
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
    ("Highest yield FIIs", {"fund_type": ["FII"], "numeric_filter": {"metric": "return", "operator": "top"}}, "ranking"),
    ("Lowest volatility funds", {"semantic_query": "low volatility", "numeric_filter": {"metric": "return", "operator": "min"}}, "ranking"),
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
    (" > 10k investors", {"numeric_filter": {"metric": "holders", "operator": "min", "value": 10000}}, "numeric"),
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
        "expected_response_type": "list_results",
        "description": f"Intermediate {cat}",
        "category": cat,
        "tier": "intermediate",
        "validation_type": "criteria_match"
    })

# --- Tier 3: Advanced (50) ---
advanced_templates = [
    # Ambiguous (10)
    ("Funds dealing with Dolar", {"fund_legal_name": "Dolar", "investment_class": "Cambial"}, "ambiguous_name_type"),
    ("Give me Verde funds", {"service_provider_entity": ["Verde"], "fund_legal_name": "Verde"}, "ambiguous_provider_name"),
    ("Funds named Strategy", {"fund_legal_name": "Strategy"}, "tricky_name"),
    ("Funds focusing on Credit", {"investment_class": "Renda Fixa", "semantic_query": "credito privado"}, "ambiguous_class"),
    ("Real Estate funds", {"fund_type": ["FII"], "semantic_query": "imobiliario"}, "ambiguous_type"),
    ("Funds investing in Gold", {"semantic_query": "gold ouro", "investment_class": "Multimercado"}, "ambiguous_asset"),
    ("Funds for kids", {"target_audience": ["RETAIL"], "semantic_query": "menores idade"}, "ambiguous_audience"),
    ("Safe funds", {"investment_class": "Renda Fixa", "semantic_query": "safe conservador"}, "ambiguous_risk"),
    ("Aggressive funds", {"investment_class": "Ações", "semantic_query": "aggressive agressivo"}, "ambiguous_risk"),
    ("Global funds", {"investment_class": "Dívida Externa", "semantic_query": "global internacional"}, "ambiguous_class"),

    # Specific Requested by User (2)
    ("Give me Bradesco Gold Fund", {"fund_legal_name": "Bradesco", "semantic_query": "gold ouro"}, "hybrid_specific"),
    ("Search for funds investing in latam tech", {"semantic_query": "technology tech latin america latam"}, "hybrid_specific"),

    # Complex Logic (18)
    ("Non-exclusive equity retail", {"is_exclusive_fund": False, "investment_class": "Ações", "target_audience": ["RETAIL"]}, "complex_boolean"),
    ("FIPs not for pros", {"fund_type": ["FIP"], "target_audience": ["QUALIFIED", "RETAIL"]}, "complex_negation"),
    ("Itau funds but not multimarket", {"service_provider_entity": ["Itau"], "investment_class": None}, "negation"),
    ("Funds holding Vale AND Petrobras", {"asset_name": ["Vale", "Petrobras"]}, "multi_holding"),
    ("Equity funds OR Fixed Income", {"investment_class": ["Ações", "Renda Fixa"]}, "multi_class"),
    ("Top 5 funds excl. Itau", {"numeric_filter": {"metric": "return", "operator": "top", "top_n": 5}}, "negation_provider"),
    ("Funds with fee < 1% AND > 1B AUM", {"numeric_filter": {"metric": "aum", "operator": "min"}}, "multi_numeric"),
    ("Exclusive funds from Bradesco or Itau", {"is_exclusive_fund": True, "service_provider_entity": ["Bradesco", "Itau"]}, "multi_provider"),
    ("Funds holding tech stocks", {"semantic_query": "tech stocks", "asset_type": ["EQUITY"]}, "semantic_holding"),
    ("Funds launched recently", {"semantic_query": "recent launch novo"}, "temporal"),
    ("Funds with liquidity D+0", {"semantic_query": "liquidez diaria d+0"}, "liquidity"),
    ("Funds with exit fee", {"numeric_filter": {"metric": "exit_fee", "operator": "min", "value": 0}}, "fee_type"),
    ("Master funds", {"semantic_query": "master"}, "structure"),
    ("Feeder funds", {"semantic_query": "feeder fic"}, "structure"),
    ("Restricted funds", {"is_exclusive_fund": True}, "access"),
    ("Funds for non-residents", {"semantic_query": "investidor nao residente"}, "audience"),
    ("Funds with currency hedge", {"semantic_query": "hedge cambial"}, "strategy"),
    ("Funds tracking the IMA-B 5", {"semantic_query": "IMA-B 5", "numeric_filter": {"benchmark_name": "IMA-B 5"}}, "specific_benchmark"),
    
    # Semantic Strategy (10)
    ("Funds investing in water", {"semantic_query": "water agua"}, "thematic"),
    ("Funds investing in uranium", {"semantic_query": "uranium uranio"}, "thematic"),
    ("Funds investing in lithium", {"semantic_query": "lithium litio"}, "thematic"),
    ("Funds investing in metaverse", {"semantic_query": "metaverse metaverso"}, "thematic"),
    ("Funds investing in AI", {"semantic_query": "artificial intelligence inteligencia artificial"}, "thematic"),
    ("Funds investing in robotics", {"semantic_query": "robotics robotica"}, "thematic"),
    ("Funds investing in space", {"semantic_query": "space espaco"}, "thematic"),
    ("Funds investing in gaming", {"semantic_query": "gaming games"}, "thematic"),
    ("Funds investing in biotech", {"semantic_query": "biotech biotecnologia"}, "thematic"),
    ("Funds investing in clean energy", {"semantic_query": "clean energy energia limpa"}, "thematic"),
]

for q, crit, cat in advanced_templates:
    queries.append({
        "query": q,
        "expected_criteria": crit,
        "expected_response_type": "list_results",
        "description": f"Advanced {cat}",
        "category": cat,
        "tier": "advanced",
        "validation_type": "criteria_match"
    })

# --- Tier 4: Edge / Vague / Error (80) ---
# Expanding "Too Vague" significantly to be fund-specific as requested
vague_templates = [
    # Fund-Specific Vague (20)
    ("List all funds", {}, "too_many_results"),
    ("Show me funds", {}, "too_many_results"),
    ("I want funds", {}, "too_many_results"),
    ("Find funds", {}, "too_many_results"),
    ("All funds in Brazil", {}, "too_many_results"),
    ("Give me top funds", {}, "ambiguous_ranking"), # Top by what?
    ("Best funds", {}, "ambiguous_ranking"),
    ("Worst funds", {}, "ambiguous_ranking"),
    ("Good funds", {}, "ambiguous_quality"),
    ("Bad funds", {}, "ambiguous_quality"),
    ("Safe investments", {}, "ambiguous_risk"),
    ("Risky investments", {}, "ambiguous_risk"),
    ("Cheap funds", {}, "ambiguous_cost"),
    ("Expensive funds", {}, "ambiguous_cost"),
    ("Funds with high return", {}, "ambiguous_ranking"), # Needs period
    ("Funds with low return", {}, "ambiguous_ranking"),
    ("Popular funds", {}, "ambiguous_popularity"),
    ("New funds", {}, "ambiguous_temporal"),
    ("Old funds", {}, "ambiguous_temporal"),
    ("Big funds", {}, "ambiguous_size"),

    # Misspellings / Human Error (20)
    ("Eqity fnds", {"investment_class": "Ações"}, "typo"),
    ("Fixed incom", {"investment_class": "Renda Fixa"}, "typo"),
    ("Multimrket", {"investment_class": "Multimercado"}, "typo"),
    ("Bradsco", {"service_provider_entity": ["Bradesco"]}, "typo"),
    ("Itauu", {"service_provider_entity": ["Itau"]}, "typo"),
    ("Santndr", {"service_provider_entity": ["Santander"]}, "typo"),
    ("Acoes fndos", {"investment_class": "Ações"}, "typo"),
    ("Renda Fixa fnds", {"investment_class": "Renda Fixa"}, "typo"),
    ("Cripto fnds", {"semantic_query": "crypto"}, "typo"),
    ("Bitcion fnds", {"semantic_query": "bitcoin"}, "typo"),
    ("Tech fnds", {"semantic_query": "technology"}, "typo"),
    ("Gld fnds", {"semantic_query": "gold"}, "typo"),
    ("ESG fnds", {"semantic_query": "ESG"}, "typo"),
    ("Smll cap", {"semantic_query": "small caps"}, "typo"),
    ("Dividnds", {"semantic_query": "dividends"}, "typo"),
    ("Petr4 fnds", {"asset_tickers": ["PETR4"]}, "typo"),
    ("Vale3 fnds", {"asset_tickers": ["VALE3"]}, "typo"),
    ("Itub4 fnds", {"asset_tickers": ["ITUB4"]}, "typo"),
    ("Bbas3 fnds", {"asset_tickers": ["BBAS3"]}, "typo"),
    ("Abev3 fnds", {"asset_tickers": ["ABEV3"]}, "typo"),

    # Conversational / General Vague (10)
    ("Invest", {}, "too_vague"),
    ("Money", {}, "too_vague"),
    ("Help me", {}, "too_vague"),
    ("Hello", {}, "greeting"),
    ("Hi", {}, "greeting"),
    ("Who are you?", {}, "identity"),
    ("Thanks", {}, "closing"),
    ("Bye", {}, "closing"),
    ("Explain FII", {}, "informational"),
    ("What is a fund?", {}, "informational"),

    # Off-topic (10)
    ("Weather", {}, "off_topic"),
    ("Cake recipe", {}, "off_topic"),
    ("President", {}, "off_topic"),
    ("Buy bitcoin", {}, "off_topic"),
    ("Stock price", {}, "market_data"),
    ("Dollar rate", {}, "market_data"),
    ("Selic", {}, "market_data"),
    ("Inflation", {}, "market_data"),
    ("GDP", {}, "market_data"),
    ("Sports", {}, "off_topic"),

    # Follow-ups (20)
    ("More", {}, "followup"),
    ("Next 10", {}, "followup"),
    ("Cheaper", {}, "followup_refine"),
    ("Better", {}, "followup_refine"),
    ("Only Itau", {}, "followup_refine"),
    ("Remove FIP", {}, "followup_refine"),
    ("Add Bradesco", {}, "followup_refine"),
    ("What about Vale?", {}, "followup_refine"),
    ("Details", {}, "followup_action"),
    ("Compare", {}, "followup_action"),
    ("Top 5", {}, "followup_refine"),
    ("Worst 5", {}, "followup_refine"),
    ("Riskier", {}, "followup_refine"),
    ("Safer", {}, "followup_refine"),
    ("Bigger", {}, "followup_refine"),
    ("Smaller", {}, "followup_refine"),
    ("Newer", {}, "followup_refine"),
    ("Older", {}, "followup_refine"),
    ("Different manager", {}, "followup_refine"),
    ("Different class", {}, "followup_refine"),
]

for q, crit, cat in vague_templates:
    # Logic for expected response type
    if cat == "too_many_results":
        rtype = "too_many_results" # Explicitly list all/top funds without criteria -> too many
    elif "ambiguous" in cat:
        rtype = "followup" # Needs clarification (top by what?)
    elif cat == "typo":
        rtype = "list_results" # Should handle typo and return results
    elif cat == "too_vague":
        rtype = "followup"
    elif cat in ["greeting", "identity", "closing", "informational"]:
        rtype = "informational"
    elif cat in ["off_topic", "market_data"]:
        rtype = "no_results" # or off_topic
    elif "followup" in cat:
        rtype = "list_results" # Context dependent
    else:
        rtype = "no_results"

    queries.append({
        "query": q,
        "expected_criteria": crit,
        "expected_response_type": rtype,
        "description": f"Vague/Error {cat}",
        "category": cat,
        "tier": "edge_case",
        "validation_type": "response_type_match"
    })

# Write to JSONL
with open("src/evaluation/data/proposed_queries_250.jsonl", "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

print(f"Generated {len(queries)} queries.")

