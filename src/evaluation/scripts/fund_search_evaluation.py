"""
Fund Search Agent Evaluation Dataset - High-Value Test Cases
=================================================================

Each query has specific evaluation criteria based on what we're testing:

EVALUATION TYPES:
1. intent_match: Check if intents list matches expected
2. extraction_match: Check if extracted criteria match expected
3. search_query_quality: Check semantic search query quality
4. response_type_match: Check if response_type is correct (for edge cases)
5. ambiguity_detection: Check if is_potentially_ambiguous flag is correct
6. context_status_match: Check if context handling is correct

Each query includes:
- query: The user input
- expected_intents: List of expected intents
- expected_extraction: Dict of expected extracted fields
- expected_response_type: What response_type should be returned
- evaluation_type: Primary evaluation method
- why_tricky: Explanation of what makes this query valuable for testing
- tier: difficulty level (1=basic, 2=intermediate, 3=advanced, 4=edge)
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional

# =============================================================================
# DATA STRUCTURE
# =============================================================================
@dataclass
class EvalQuery:
    query: str
    expected_intents: list[str]
    expected_extraction: dict
    expected_response_type: str
    evaluation_type: str
    why_tricky: str
    tier: int
    category: str
    # Optional fields for specific evaluations
    expected_search_query_contains: list[str] = None  # Keywords that should be in search_query
    expected_required_name_terms: list[str] = None
    expected_ambiguous: bool = None
    expected_context_status: str = None
    expected_language: str = None
    history_context: str = None  # For multi-turn tests

queries = []

# =============================================================================
# TIER 1: BASIC QUERIES (60 queries)
# These should be correctly handled with high accuracy
# =============================================================================

# --- 1.1 PURE CRITERIA SEARCH (20 queries) ---
# Tests: find_by_criteria intent + extraction accuracy
basic_criteria = [
    # Fund Type
    EvalQuery(
        query="FIP funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FIP"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Direct fund type filter",
        tier=1, category="fund_type"
    ),
    EvalQuery(
        query="Show me FII funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FII"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Direct fund type with conversational prefix",
        tier=1, category="fund_type"
    ),
    EvalQuery(
        query="FIDC",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FIDC"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Single word fund type",
        tier=1, category="fund_type"
    ),
    EvalQuery(
        query="ETF funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["ETF"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="ETF type",
        tier=1, category="fund_type"
    ),
    
    # Investment Class
    EvalQuery(
        query="Equity funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Ações"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="English to Portuguese class translation",
        tier=1, category="investment_class",
        expected_language="en"
    ),
    EvalQuery(
        query="Fundos de ações",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Ações"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese query",
        tier=1, category="investment_class",
        expected_language="pt"
    ),
    EvalQuery(
        query="Fixed income funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Fixed income translation",
        tier=1, category="investment_class"
    ),
    EvalQuery(
        query="Renda fixa",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese investment class",
        tier=1, category="investment_class"
    ),
    EvalQuery(
        query="Multimarket funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Multimercado"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Multimarket translation",
        tier=1, category="investment_class"
    ),
    EvalQuery(
        query="Cambial funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Cambial"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Currency funds",
        tier=1, category="investment_class"
    ),
    
    # Target Audience
    EvalQuery(
        query="Funds for qualified investors",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["QUALIFIED"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Qualified investor filter",
        tier=1, category="audience"
    ),
    EvalQuery(
        query="Professional investor funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["PROFESSIONAL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Professional investor filter",
        tier=1, category="audience"
    ),
    EvalQuery(
        query="Retail funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["RETAIL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Retail investor filter",
        tier=1, category="audience"
    ),
    EvalQuery(
        query="Fundos para investidor qualificado",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["QUALIFIED"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese audience filter",
        tier=1, category="audience"
    ),
    
    # Boolean Flags
    EvalQuery(
        query="Exclusive funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"is_exclusive_fund": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Boolean flag extraction",
        tier=1, category="boolean"
    ),
    EvalQuery(
        query="Funds with long term taxation",
        expected_intents=["find_by_criteria"],
        expected_extraction={"has_long_term_taxation": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Tax benefit flag",
        tier=1, category="boolean"
    ),
    EvalQuery(
        query="Fund of funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_of_funds": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="FoF flag",
        tier=1, category="boolean"
    ),
    EvalQuery(
        query="FIC funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_of_funds": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="FIC = Fund of funds",
        tier=1, category="boolean"
    ),
    EvalQuery(
        query="Funds that can invest 100% abroad",
        expected_intents=["find_by_criteria"],
        expected_extraction={"can_invest_abroad_100_pct": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="International investment flag",
        tier=1, category="boolean"
    ),
    EvalQuery(
        query="Fundos exclusivos",
        expected_intents=["find_by_criteria"],
        expected_extraction={"is_exclusive_fund": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese boolean flag",
        tier=1, category="boolean"
    ),
]
queries.extend(basic_criteria)

# --- 1.2 PURE NAME SEARCH (15 queries) ---
# Tests: find_by_name intent + semantic_query + required_name_terms
basic_names = [
    EvalQuery(
        query="Alaska Black",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "alaska black"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Famous fund name - should NOT interpret as strategy",
        tier=1, category="fund_name",
        expected_required_name_terms=["alaska", "black"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Verde Scena",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "verde scena"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Famous fund name",
        tier=1, category="fund_name",
        expected_required_name_terms=["verde", "scena"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Dynamo Cougar",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "dynamo cougar"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Famous fund name with animal",
        tier=1, category="fund_name",
        expected_required_name_terms=["dynamo", "cougar"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="SPX Nimitz",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "spx nimitz"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Famous fund name",
        tier=1, category="fund_name",
        expected_required_name_terms=["spx", "nimitz"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Kapitalo Kappa",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "kapitalo kappa"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Famous fund name",
        tier=1, category="fund_name",
        expected_required_name_terms=["kapitalo", "kappa"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Ibiuna Hedge",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "ibiuna hedge"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Fund name with strategy word (hedge)",
        tier=1, category="fund_name",
        expected_required_name_terms=["ibiuna", "hedge"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Occam Retorno Absoluto",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "occam retorno absoluto"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Full fund name with strategy description",
        tier=1, category="fund_name",
        expected_required_name_terms=["occam"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="JGP Strategy",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "jgp strategy"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Fund name with generic word (strategy)",
        tier=1, category="fund_name",
        expected_required_name_terms=["jgp", "strategy"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Truxt Long Short",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "truxt long short"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Fund name with strategy type",
        tier=1, category="fund_name",
        expected_required_name_terms=["truxt"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Adam Macro",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "adam macro"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Manager name + strategy as fund name",
        tier=1, category="fund_name",
        expected_required_name_terms=["adam", "macro"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Ace Capital",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "ace capital"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Manager name",
        tier=1, category="fund_name",
        expected_required_name_terms=["ace", "capital"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Bahia Asset",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "bahia asset"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Geographic manager name",
        tier=1, category="fund_name",
        expected_required_name_terms=["bahia"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Giant Steps",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "giant steps"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="English fund name",
        tier=1, category="fund_name",
        expected_required_name_terms=["giant", "steps"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Moat Capital",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "moat capital"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="English fund name",
        tier=1, category="fund_name",
        expected_required_name_terms=["moat"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="XP Selection",
        expected_intents=["find_by_name"],
        expected_extraction={"semantic_query": "xp selection"},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Manager prefix fund name",
        tier=1, category="fund_name",
        expected_required_name_terms=["xp", "selection"],
        expected_ambiguous=False
    ),
]
queries.extend(basic_names)

# --- 1.3 PURE MANAGER/PROVIDER SEARCH (15 queries) ---
# Tests: find_by_criteria intent + service_provider_entity extraction
basic_manager = [
    EvalQuery(
        query="Itau funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Major bank manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Bradesco funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Major bank manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="BTG Pactual funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["BTG Pactual"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Investment bank manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="XP Asset funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["XP"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Platform manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Kinea funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Kinea"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Asset manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Vinci Partners funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Vinci Partners"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="PE/VC manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Safra funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Safra"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Private bank manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Santander funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Santander"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="International bank manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="BB Asset funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["BB Asset"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="State bank manager (abbreviation)",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Caixa funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Caixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="State bank manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Credit Suisse funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Credit Suisse"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="International manager (now UBS)",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Fundos da JGP",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["JGP"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese query with manager acronym",
        tier=1, category="manager",
        expected_language="pt"
    ),
    EvalQuery(
        query="SPX Capital funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["SPX"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Hedge fund manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Funds from Nubank",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Nu Asset", "Nubank"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Fintech manager",
        tier=1, category="manager"
    ),
    EvalQuery(
        query="Rio Bravo funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Rio Bravo"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Independent manager with geographic name",
        tier=1, category="manager"
    ),
]
queries.extend(basic_manager)

# --- 1.4 PURE EXPOSURE SEARCH (10 queries) ---
# Tests: find_by_exposure intent + asset extraction
basic_exposure = [
    EvalQuery(
        query="Funds holding Petrobras",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["Petrobras"], "asset_tickers": ["PETR3", "PETR4"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Brazilian blue chip",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Funds with Vale",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["Vale"], "asset_tickers": ["VALE3"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Mining company",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Exposure to ITUB4",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_tickers": ["ITUB4"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Direct ticker query",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Funds invested in Ambev",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["Ambev"], "asset_tickers": ["ABEV3"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Consumer company",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Funds with BBAS3",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_tickers": ["BBAS3"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Bank ticker",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Funds holding WEG",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["WEG"], "asset_tickers": ["WEGE3"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Industrial company",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Funds with Magazine Luiza",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["Magazine Luiza"], "asset_tickers": ["MGLU3"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Retail company",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Exposure to Tesla",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["Tesla"], "asset_tickers": ["TSLA34"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Foreign stock (BDR)",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Funds with Apple shares",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["Apple"], "asset_tickers": ["AAPL34"], "asset_type": ["EQUITY"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Foreign stock with asset type hint",
        tier=1, category="exposure"
    ),
    EvalQuery(
        query="Funds holding government bonds",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_type": ["FIXED_INCOME"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Asset type without specific name",
        tier=1, category="exposure"
    ),
]
queries.extend(basic_exposure)

# =============================================================================
# TIER 2: INTERMEDIATE QUERIES (70 queries)
# Multi-criteria, numeric filters, combinations
# =============================================================================

# --- 2.1 DUAL CRITERIA COMBINATIONS (25 queries) ---
intermediate_dual = [
    EvalQuery(
        query="Equity funds from Itau",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Ações"], "service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Class + manager combination",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Fixed income for qualified investors",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"], "target_audience": ["QUALIFIED"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Class + audience combination",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Multimarket funds from BTG",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Multimercado"], "service_provider_entity": ["BTG"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Class + manager",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="FII from Kinea",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FII"], "service_provider_entity": ["Kinea"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Type + manager",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Exclusive equity funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Ações"], "is_exclusive_fund": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Class + boolean",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="FIP for professional investors",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FIP"], "target_audience": ["PROFESSIONAL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Type + audience",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Retail cambial funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Cambial"], "target_audience": ["RETAIL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Class + audience",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Long term taxation Bradesco",
        expected_intents=["find_by_criteria"],
        expected_extraction={"has_long_term_taxation": True, "service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Boolean + manager",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Non-exclusive multimarket",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Multimercado"], "is_exclusive_fund": False},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Class + negative boolean",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="FII retail",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FII"], "target_audience": ["RETAIL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Type + audience minimal",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Ibiuna fixed income",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Ibiuna"], "investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager + class",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="SPX multimarket",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["SPX"], "investment_class": ["Multimercado"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager + class minimal",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Vinci Partners FIP",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Vinci Partners"], "fund_type": ["FIP"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager + type",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Safra retail funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Safra"], "target_audience": ["RETAIL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager + audience",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Opportunity qualified",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Opportunity"], "target_audience": ["QUALIFIED"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager + audience - manager name sounds generic",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="XP exclusive funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["XP"], "is_exclusive_fund": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager + boolean",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Fundos de ações BTG qualificado",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Ações"], "service_provider_entity": ["BTG"], "target_audience": ["QUALIFIED"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Triple criteria in Portuguese",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="FII logistics Kinea",
        expected_intents=["find_by_criteria", "find_by_strategy"],
        expected_extraction={"fund_type": ["FII"], "service_provider_entity": ["Kinea"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Type + manager + semantic theme",
        tier=2, category="dual_criteria",
        expected_search_query_contains=["logistica", "galpao"]
    ),
    EvalQuery(
        query="ETF equity",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["ETF"], "investment_class": ["Ações"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Type + class",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="FIDC with long term tax",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FIDC"], "has_long_term_taxation": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Type + boolean",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Fundos multimercado exclusivos Itau",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Multimercado"], "is_exclusive_fund": True, "service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Triple criteria Portuguese",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Foreign debt retail",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Dívida Externa"], "target_audience": ["RETAIL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Foreign debt class + audience",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Short term Santander",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Curto Prazo"], "service_provider_entity": ["Santander"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Short term class + manager",
        tier=2, category="dual_criteria"
    ),
    EvalQuery(
        query="Referenciado DI Caixa",
        expected_intents=["find_by_criteria", "find_by_strategy"],
        expected_extraction={"investment_class": ["Referenciado"], "service_provider_entity": ["Caixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Referenciado class + manager + strategy hint",
        tier=2, category="dual_criteria",
        expected_search_query_contains=["di", "cdi"]
    ),
    EvalQuery(
        query="BB Asset funds for professionals 100% abroad",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["BB Asset"], "target_audience": ["PROFESSIONAL"], "can_invest_abroad_100_pct": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager + audience + boolean",
        tier=2, category="dual_criteria"
    ),
]
queries.extend(intermediate_dual)

# --- 2.2 NUMERIC FILTER QUERIES (25 queries) ---
intermediate_numeric = [
    EvalQuery(
        query="Top 10 equity funds",
        expected_intents=["find_by_criteria", "has_numeric_filter"],
        expected_extraction={"investment_class": ["Ações"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 10}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Class + ranking",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Best fixed income funds",
        expected_intents=["find_by_criteria", "has_numeric_filter"],
        expected_extraction={"investment_class": ["Renda Fixa"], "numeric_filter": {"metric": "return", "operator": "top"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Best = top by return",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Funds with lowest fee",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "management_fee", "operator": "min"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Lowest fee",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Largest funds by AUM",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Largest = max AUM",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Top 5 FIIs",
        expected_intents=["find_by_criteria", "has_numeric_filter"],
        expected_extraction={"fund_type": ["FII"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 5}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Top N + type",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Best multimarket 12 months",
        expected_intents=["find_by_criteria", "has_numeric_filter"],
        expected_extraction={"investment_class": ["Multimercado"], "numeric_filter": {"metric": "return", "operator": "top", "performance_period": "12m"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Best + class + period",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Worst performing funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "min"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Worst = min return",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Most popular funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "holders", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Popular = max holders",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Top 10 Itau funds",
        expected_intents=["find_by_criteria", "has_numeric_filter"],
        expected_extraction={"service_provider_entity": ["Itau"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 10}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Top N + manager",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Best funds YTD",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "top", "performance_period": "ytd"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="YTD period",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Funds with fee less than 1%",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "management_fee", "operator": "max", "value": 1.0}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Fee threshold",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="AUM greater than 1 billion",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "min", "value": 1000000000}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="AUM threshold with billion",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Funds with more than 10000 investors",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "holders", "operator": "min", "value": 10000}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Holders threshold",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Funds that beat CDI",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "min", "benchmark_name": "CDI"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Benchmark comparison",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Funds that beat Ibovespa",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "min", "benchmark_name": "IBOVESPA"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Ibovespa benchmark",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Zero fee funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "management_fee", "operator": "exact", "value": 0}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Exact zero value",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Fee around 2%",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "management_fee", "operator": "around", "value": 2.0}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Approximate value",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Return greater than 10% last year",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "min", "value": 10, "performance_period": "12m"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Return threshold + period",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="AUM between 100M and 1B",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "range", "value": 100000000, "max_value": 1000000000}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Range filter",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Minimum investment under 1000 reais",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "min_investment", "operator": "max", "value": 1000}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Min investment threshold",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Funds with performance fee",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "performance_fee", "operator": "min", "value": 0}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Has performance fee (>0)",
        tier=2, category="numeric"
    ),
    EvalQuery(
        query="Top 3 funds holding Vale",
        expected_intents=["find_by_exposure", "has_numeric_filter"],
        expected_extraction={"asset_name": ["Vale"], "numeric_filter": {"metric": "return", "operator": "top", "top_n": 3}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Top N + exposure",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Cheapest equity funds",
        expected_intents=["find_by_criteria", "has_numeric_filter"],
        expected_extraction={"investment_class": ["Ações"], "numeric_filter": {"metric": "management_fee", "operator": "min"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Cheapest = min fee + class",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Best funds last 3 years",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "top", "performance_period": "36m"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="3 years = 36m",
        tier=2, category="ranking"
    ),
    EvalQuery(
        query="Maiores fundos por patrimonio",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese AUM ranking",
        tier=2, category="ranking",
        expected_language="pt"
    ),
]
queries.extend(intermediate_numeric)

# --- 2.3 THEMATIC/STRATEGY SEARCH (20 queries) ---
intermediate_thematic = [
    EvalQuery(
        query="Crypto funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Thematic search - crypto",
        tier=2, category="thematic",
        expected_search_query_contains=["cripto", "bitcoin", "blockchain"]
    ),
    EvalQuery(
        query="ESG funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Thematic search - ESG",
        tier=2, category="thematic",
        expected_search_query_contains=["esg", "sustentavel", "sustentabilidade"]
    ),
    EvalQuery(
        query="Tech funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Thematic search - technology",
        tier=2, category="thematic",
        expected_search_query_contains=["tecnologia", "tech"]
    ),
    EvalQuery(
        query="Gold funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Commodity theme - gold",
        tier=2, category="thematic",
        expected_search_query_contains=["ouro", "gold"]
    ),
    EvalQuery(
        query="Infrastructure funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Thematic - infrastructure",
        tier=2, category="thematic",
        expected_search_query_contains=["infraestrutura", "infra"]
    ),
    EvalQuery(
        query="Small cap funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - small caps",
        tier=2, category="thematic",
        expected_search_query_contains=["small", "cap", "pequenas"]
    ),
    EvalQuery(
        query="Dividend funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - dividends",
        tier=2, category="thematic",
        expected_search_query_contains=["dividendo", "dividend"]
    ),
    EvalQuery(
        query="Agro funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Sector - agribusiness",
        tier=2, category="thematic",
        expected_search_query_contains=["agro", "agronegocio"]
    ),
    EvalQuery(
        query="Real estate paper funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="FII strategy - CRI/CRA",
        tier=2, category="thematic",
        expected_search_query_contains=["papel", "cri", "recebivel"]
    ),
    EvalQuery(
        query="Long short funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - long short",
        tier=2, category="thematic",
        expected_search_query_contains=["long", "short"]
    ),
    EvalQuery(
        query="Macro funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - macro",
        tier=2, category="thematic",
        expected_search_query_contains=["macro"]
    ),
    EvalQuery(
        query="Hedge funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - hedge",
        tier=2, category="thematic",
        expected_search_query_contains=["hedge"]
    ),
    EvalQuery(
        query="Private credit funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - private credit",
        tier=2, category="thematic",
        expected_search_query_contains=["credito", "privado"]
    ),
    EvalQuery(
        query="Index funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - passive/index",
        tier=2, category="thematic",
        expected_search_query_contains=["indice", "passivo"]
    ),
    EvalQuery(
        query="High yield funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - high yield",
        tier=2, category="thematic",
        expected_search_query_contains=["high", "yield", "alto"]
    ),
    EvalQuery(
        query="Inflation linked funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - inflation",
        tier=2, category="thematic",
        expected_search_query_contains=["inflacao", "ipca", "ima-b"]
    ),
    EvalQuery(
        query="Value investing funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - value",
        tier=2, category="thematic",
        expected_search_query_contains=["value", "valor"]
    ),
    EvalQuery(
        query="Growth funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - growth",
        tier=2, category="thematic",
        expected_search_query_contains=["growth", "crescimento"]
    ),
    EvalQuery(
        query="Quantitative funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - quant",
        tier=2, category="thematic",
        expected_search_query_contains=["quant", "quantitativo", "sistematico"]
    ),
    EvalQuery(
        query="Event driven funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Strategy - event driven",
        tier=2, category="thematic",
        expected_search_query_contains=["event", "evento", "situacoes"]
    ),
]
queries.extend(intermediate_thematic)

# =============================================================================
# TIER 3: ADVANCED/AMBIGUOUS QUERIES (80 queries)
# The core test cases - manager+theme, disambiguation, tricky interpretation
# =============================================================================

# --- 3.1 MANAGER + THEME AMBIGUITY (35 queries) ---
# These are the HARDEST cases - should interpret as strategy not literal name
advanced_manager_theme = [
    EvalQuery(
        query="bradesco gold fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Bradesco + Gold = Bradesco Ouro FI, NOT literal 'Bradesco Gold'",
        tier=3, category="manager_theme",
        expected_search_query_contains=["bradesco", "ouro"],
        expected_required_name_terms=["bradesco"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="itau tech fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Itau + tech sector, NOT literal 'Itau Tech'",
        tier=3, category="manager_theme",
        expected_search_query_contains=["itau", "tecnologia"],
        expected_required_name_terms=["itau"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="btg crypto fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["BTG"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="BTG + crypto theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["btg", "cripto"],
        expected_required_name_terms=["btg"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="xp bitcoin",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["XP"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="XP + bitcoin theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["xp", "bitcoin"],
        expected_required_name_terms=["xp"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="safra silver fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Safra"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Safra + silver commodity",
        tier=3, category="manager_theme",
        expected_search_query_contains=["safra", "prata"],
        expected_required_name_terms=["safra"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="bradesco healthcare",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Bradesco + healthcare sector",
        tier=3, category="manager_theme",
        expected_search_query_contains=["bradesco", "saude"],
        expected_required_name_terms=["bradesco"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="santander agro fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Santander"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Santander + agro theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["santander", "agro"],
        expected_required_name_terms=["santander"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="bb infra",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["BB"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="BB + infrastructure theme (abbreviation)",
        tier=3, category="manager_theme",
        expected_search_query_contains=["bb", "infraestrutura"],
        expected_required_name_terms=["bb"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="caixa real estate",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Caixa"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Caixa + real estate theme (not FII type)",
        tier=3, category="manager_theme",
        expected_search_query_contains=["caixa", "imobiliario"],
        expected_required_name_terms=["caixa"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="itau esg fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Itau + ESG theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["itau", "esg"],
        expected_required_name_terms=["itau"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="bradesco sustainable",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Bradesco + sustainability theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["bradesco", "sustentavel"],
        expected_required_name_terms=["bradesco"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="xp dividendos",
        expected_intents=["find_by_name", "find_by_strategy"],
        expected_extraction={"service_provider_entity": ["XP"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Could be exact fund name 'XP Dividendos' OR strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["xp", "dividendo"],
        expected_required_name_terms=["xp", "dividendos"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="itau income fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Itau + income/dividend strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["itau", "renda"],
        expected_required_name_terms=["itau"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="btg oil fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["BTG"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="BTG + oil/energy theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["btg", "petroleo"],
        expected_required_name_terms=["btg"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="safra commodities",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Safra"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Safra + commodities theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["safra", "commodities"],
        expected_required_name_terms=["safra"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="itau small caps",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Itau + small caps strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["itau", "small"],
        expected_required_name_terms=["itau"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="bradesco value",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Bradesco + value investing strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["bradesco", "value", "valor"],
        expected_required_name_terms=["bradesco"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="xp growth fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["XP"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="XP + growth strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["xp", "growth", "crescimento"],
        expected_required_name_terms=["xp"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="itau credit fund",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Itau + private credit strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["itau", "credito"],
        expected_required_name_terms=["itau"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="bradesco high yield",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Bradesco + high yield strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["bradesco", "high", "yield"],
        expected_required_name_terms=["bradesco"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="safra inflation",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Safra"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Safra + inflation-linked strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["safra", "inflacao", "ipca"],
        expected_required_name_terms=["safra"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="kinea real estate",
        expected_intents=["find_by_strategy", "find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Kinea"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Kinea has many FIIs - is this FII type or just theme?",
        tier=3, category="manager_theme",
        expected_search_query_contains=["kinea", "imobiliario"],
        expected_required_name_terms=["kinea"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="vinci infrastructure",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Vinci"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Vinci + infrastructure theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["vinci", "infraestrutura"],
        expected_required_name_terms=["vinci"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="xp industrial",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["XP"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="XP + industrial real estate theme",
        tier=3, category="manager_theme",
        expected_search_query_contains=["xp", "industrial", "logistica"],
        expected_required_name_terms=["xp"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="verde macro",
        expected_intents=["find_by_name", "find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Verde"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Verde + macro strategy - could be name or strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["verde", "macro"],
        expected_required_name_terms=["verde"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="spx long bias",
        expected_intents=["find_by_name", "find_by_strategy"],
        expected_extraction={"service_provider_entity": ["SPX"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="SPX + long bias strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["spx", "long", "bias"],
        expected_required_name_terms=["spx"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="kapitalo systematic",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Kapitalo"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Kapitalo + systematic/quant strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["kapitalo", "sistematico"],
        expected_required_name_terms=["kapitalo"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="ibiuna credit",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Ibiuna"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Ibiuna + credit strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["ibiuna", "credito"],
        expected_required_name_terms=["ibiuna"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="jgp long only",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["JGP"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="JGP + long only strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["jgp", "long", "only"],
        expected_required_name_terms=["jgp"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="occam absolute return",
        expected_intents=["find_by_name"],
        expected_extraction={"service_provider_entity": ["Occam"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Occam Retorno Absoluto is actual fund name",
        tier=3, category="manager_theme",
        expected_search_query_contains=["occam", "retorno", "absoluto"],
        expected_required_name_terms=["occam"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="bahia long short",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Bahia"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Bahia Asset + long short strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["bahia", "long", "short"],
        expected_required_name_terms=["bahia"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="ace small cap",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Ace"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Ace Capital + small cap strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["ace", "small"],
        expected_required_name_terms=["ace"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="truxt valor",
        expected_intents=["find_by_name", "find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Truxt"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Truxt + value/valor - could be name",
        tier=3, category="manager_theme",
        expected_search_query_contains=["truxt", "valor"],
        expected_required_name_terms=["truxt"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="moat dividend",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Moat"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Moat Capital + dividend strategy",
        tier=3, category="manager_theme",
        expected_search_query_contains=["moat", "dividendo"],
        expected_required_name_terms=["moat"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="giant steps trend",
        expected_intents=["find_by_strategy"],
        expected_extraction={"service_provider_entity": ["Giant Steps"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Giant Steps + trend following",
        tier=3, category="manager_theme",
        expected_search_query_contains=["giant", "trend"],
        expected_required_name_terms=["giant"],
        expected_ambiguous=True
    ),
]
queries.extend(advanced_manager_theme)

# --- 3.2 GENERIC NAMES THAT ARE ACTUALLY MANAGERS (15 queries) ---
advanced_generic_manager = [
    EvalQuery(
        query="legacy funds",
        expected_intents=["find_by_name"],
        expected_extraction={"service_provider_entity": ["Legacy Capital"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Legacy Capital is a manager - NOT 'old' funds",
        tier=3, category="generic_manager",
        expected_required_name_terms=["legacy"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="verde funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Verde"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Verde is color AND famous manager",
        tier=3, category="generic_manager",
        expected_required_name_terms=["verde"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="opportunity funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Opportunity"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Opportunity is manager name but sounds generic",
        tier=3, category="generic_manager",
        expected_required_name_terms=["opportunity"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="absolute funds",
        expected_intents=["find_by_name"],
        expected_extraction={"service_provider_entity": ["Absoluto Partners"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Absoluto Partners manager vs 'absolute return' concept",
        tier=3, category="generic_manager",
        expected_required_name_terms=["absoluto", "absolute"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="alpha funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Alpha could be manager or 'alpha seeking' strategy",
        tier=3, category="generic_manager",
        expected_search_query_contains=["alpha"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="constellation funds",
        expected_intents=["find_by_name"],
        expected_extraction={"service_provider_entity": ["Constellation"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Constellation is a real manager",
        tier=3, category="generic_manager",
        expected_required_name_terms=["constellation"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="aurora fund",
        expected_intents=["find_by_name"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Aurora could be fund name or dawn themed",
        tier=3, category="generic_manager",
        expected_required_name_terms=["aurora"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="brasil capital funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Brasil Capital"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Brasil Capital is a manager",
        tier=3, category="generic_manager",
        expected_required_name_terms=["brasil", "capital"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="patria funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Patria"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Patria Investimentos manager",
        tier=3, category="generic_manager",
        expected_required_name_terms=["patria"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="pantera fund",
        expected_intents=["find_by_name"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Could be fund name or panther themed",
        tier=3, category="generic_manager",
        expected_required_name_terms=["pantera"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="oceano fund",
        expected_intents=["find_by_name"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Could be fund name or ocean/maritime theme",
        tier=3, category="generic_manager",
        expected_required_name_terms=["oceano"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="capital funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Too generic - many managers have 'Capital' in name",
        tier=3, category="generic_manager",
        expected_ambiguous=True
    ),
    EvalQuery(
        query="investment funds",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="too_many_results",
        evaluation_type="response_type_match",
        why_tricky="Too generic - should ask for clarification",
        tier=3, category="generic_manager"
    ),
    EvalQuery(
        query="premier fund",
        expected_intents=["find_by_name"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Could be specific fund or quality descriptor",
        tier=3, category="generic_manager",
        expected_required_name_terms=["premier"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="selection fund",
        expected_intents=["find_by_name"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Could be specific fund name",
        tier=3, category="generic_manager",
        expected_required_name_terms=["selection"],
        expected_ambiguous=True
    ),
]
queries.extend(advanced_generic_manager)

# --- 3.3 COMPLEX SEMANTIC QUERIES (15 queries) ---
advanced_semantic = [
    EvalQuery(
        query="funds that invest in latam tech",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Complex theme: Latin America + technology intersection",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["latin", "america", "tecnologia"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="emerging market debt funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Complex: emerging markets + fixed income",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["emergentes", "divida"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="renewable energy funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Theme: clean/renewable energy",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["energia", "renovavel", "limpa"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds investing in water",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Niche theme: water/utilities",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["agua", "water", "saneamento"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds investing in AI",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Theme: artificial intelligence",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["inteligencia", "artificial", "ai"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds investing in metaverse",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Niche theme: metaverse",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["metaverso", "metaverse"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds investing in lithium",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Commodity theme: lithium",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["litio", "lithium"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds investing in robotics",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Theme: robotics/automation",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["robotica", "automacao"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds investing in biotech",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Theme: biotechnology",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["biotecnologia", "biotech"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds investing in gaming",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Theme: gaming/esports",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["games", "gaming", "jogos"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="conservative fixed income for seniors",
        expected_intents=["find_by_strategy", "find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Class + risk profile + demographic hint",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["conservador", "baixo", "risco"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="aggressive growth for young investors",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Risk profile + strategy + demographic",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["agressivo", "crescimento"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds with low volatility",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Risk characteristic search",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["baixa", "volatilidade"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds with daily liquidity",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Liquidity characteristic",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["liquidez", "diaria", "d+0", "d+1"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="funds with currency hedge",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Hedge characteristic",
        tier=3, category="complex_semantic",
        expected_search_query_contains=["hedge", "cambial"],
        expected_ambiguous=False
    ),
]
queries.extend(advanced_semantic)

# --- 3.4 AMBIGUOUS WORDS (15 queries) ---
advanced_ambiguous = [
    EvalQuery(
        query="Dollar funds",
        expected_intents=["find_by_strategy", "find_by_criteria"],
        expected_extraction={"investment_class": ["Cambial"]},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Dollar = Cambial class or USD exposure strategy?",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["dolar"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Credit funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Credit = credito privado strategy",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["credito", "privado"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Global funds",
        expected_intents=["find_by_strategy", "find_by_criteria"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Global = international or Dívida Externa class?",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["global", "internacional"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Safe funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Safe = subjective risk assessment",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["conservador", "baixo", "risco"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Aggressive funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Aggressive = subjective risk assessment",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["agressivo", "arrojado"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Master funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Master = fund structure type",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["master"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Feeder funds",
        expected_intents=["find_by_strategy", "find_by_criteria"],
        expected_extraction={"fund_of_funds": True},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Feeder = FIC/fund structure",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["feeder", "fic"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Paper funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Paper = FII paper (CRI/CRA) strategy",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["papel", "cri", "cra"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Brick funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Brick = FII tijolo (physical real estate)",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["tijolo", "fisico", "imovel"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Hybrid funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Hybrid = FII hybrid or balanced strategy?",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["hibrido"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Balanced funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Balanced = asset allocation strategy",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["balanceado", "misto"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Active funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Active = active management",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["ativo", "gestao"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Passive funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Passive = index/ETF style",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["passivo", "indice"],
        expected_ambiguous=False
    ),
    EvalQuery(
        query="Open funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Open = accepting new investments",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["aberto", "captacao"],
        expected_ambiguous=True
    ),
    EvalQuery(
        query="Closed funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Closed = closed for new investments",
        tier=3, category="ambiguous_word",
        expected_search_query_contains=["fechado"],
        expected_ambiguous=True
    ),
]
queries.extend(advanced_ambiguous)

# =============================================================================
# TIER 4: EDGE CASES & ERROR HANDLING (90 queries)
# Vague queries, typos, conversational, context-dependent
# =============================================================================

# --- 4.1 TOO VAGUE - SHOULD ASK FOLLOWUP (20 queries) ---
edge_vague = [
    EvalQuery(
        query="Show me funds",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="too_many_results",
        evaluation_type="response_type_match",
        why_tricky="No criteria - should ask for clarification",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="List all funds",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="too_many_results",
        evaluation_type="response_type_match",
        why_tricky="Explicitly asks for all - impossible",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="I want funds",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="No criteria",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Find funds",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="No criteria",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Give me top funds",
        expected_intents=["has_numeric_filter", "general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Top by what metric?",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Best funds",
        expected_intents=["has_numeric_filter", "general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Best by what metric?",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Good funds",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Subjective quality - need criteria",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Bad funds",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Subjective quality - need criteria",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Cheap funds",
        expected_intents=["has_numeric_filter", "general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Cheap = low fee? low min investment?",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Expensive funds",
        expected_intents=["has_numeric_filter", "general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Expensive = high fee? high min investment?",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Popular funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "holders", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Popular = high holders - should work",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="New funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="New = recently launched",
        tier=4, category="too_vague",
        expected_search_query_contains=["novo", "recente", "lancamento"]
    ),
    EvalQuery(
        query="Old funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Old = long track record",
        tier=4, category="too_vague",
        expected_search_query_contains=["antigo", "tradicional", "historico"]
    ),
    EvalQuery(
        query="Big funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Big = high AUM",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Small funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "min"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Small = low AUM",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="High return funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="High return - but what period?",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Low return funds",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "min"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Low return - but what period?",
        tier=4, category="too_vague"
    ),
    EvalQuery(
        query="Risky funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Subjective risk assessment",
        tier=4, category="too_vague",
        expected_search_query_contains=["risco", "agressivo", "volatil"]
    ),
    EvalQuery(
        query="Safe investments",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Subjective safety assessment",
        tier=4, category="too_vague",
        expected_search_query_contains=["seguro", "conservador", "baixo", "risco"]
    ),
    EvalQuery(
        query="fundos",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Single word - no criteria",
        tier=4, category="too_vague"
    ),
]
queries.extend(edge_vague)

# --- 4.2 TYPOS & MISSPELLINGS (20 queries) ---
edge_typos = [
    EvalQuery(
        query="Eqity funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Ações"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: Eqity → Equity",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="Fixed incom",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: incom → income",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="Multimrket",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Multimercado"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: Multimrket → Multimarket",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="Bradsco funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: Bradsco → Bradesco",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="Itauu funds",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: Itauu → Itau",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="Santnder",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Santander"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: Santnder → Santander",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="Cripto funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Portuguese spelling: Cripto → Crypto",
        tier=4, category="typo",
        expected_search_query_contains=["cripto"]
    ),
    EvalQuery(
        query="Bitcion",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Typo: Bitcion → Bitcoin",
        tier=4, category="typo",
        expected_search_query_contains=["bitcoin"]
    ),
    EvalQuery(
        query="Tec funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Typo: Tec → Tech",
        tier=4, category="typo",
        expected_search_query_contains=["tech", "tecnologia"]
    ),
    EvalQuery(
        query="Gld funds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Typo: Gld → Gold",
        tier=4, category="typo",
        expected_search_query_contains=["ouro", "gold"]
    ),
    EvalQuery(
        query="Smll cap",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Typo: Smll → Small",
        tier=4, category="typo",
        expected_search_query_contains=["small"]
    ),
    EvalQuery(
        query="Dividnds",
        expected_intents=["find_by_strategy"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Typo: Dividnds → Dividends",
        tier=4, category="typo",
        expected_search_query_contains=["dividendo"]
    ),
    EvalQuery(
        query="Petr4 funds",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_tickers": ["PETR4"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Lowercase ticker: Petr4 → PETR4",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="vale3 funds",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_tickers": ["VALE3"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Lowercase ticker: vale3 → VALE3",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="Alaska Blck",
        expected_intents=["find_by_name"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Typo in fund name: Blck → Black",
        tier=4, category="typo",
        expected_required_name_terms=["alaska"]
    ),
    EvalQuery(
        query="Dinamo Cougar",
        expected_intents=["find_by_name"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="intent_match",
        why_tricky="Typo: Dinamo → Dynamo",
        tier=4, category="typo",
        expected_required_name_terms=["cougar"]
    ),
    EvalQuery(
        query="qualifed investors",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["QUALIFIED"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: qualifed → qualified",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="proffesional",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["PROFESSIONAL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: proffesional → professional",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="renda fiax",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Typo: fiax → fixa",
        tier=4, category="typo"
    ),
    EvalQuery(
        query="acoes",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Ações"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Missing accent: acoes → ações",
        tier=4, category="typo"
    ),
]
queries.extend(edge_typos)

# --- 4.3 CONVERSATIONAL & INFORMATIONAL (20 queries) ---
edge_conversational = [
    EvalQuery(
        query="Hello",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Greeting - no fund search",
        tier=4, category="greeting"
    ),
    EvalQuery(
        query="Hi",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Greeting - no fund search",
        tier=4, category="greeting"
    ),
    EvalQuery(
        query="Thank you",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Gratitude - no fund search",
        tier=4, category="closing"
    ),
    EvalQuery(
        query="Bye",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Farewell - no fund search",
        tier=4, category="closing"
    ),
    EvalQuery(
        query="What is a FII?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Definition question - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="What is FIDC?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Definition question - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="Explain multimarket funds",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Explanation request - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="How do FIIs work?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="How question - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="What is the difference between FIP and FII?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Comparison question - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="Who are you?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Identity question - informational",
        tier=4, category="identity"
    ),
    EvalQuery(
        query="What can you do?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Capability question - informational",
        tier=4, category="identity"
    ),
    EvalQuery(
        query="Help",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Help request - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="What is CDI?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Financial concept - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="What is Selic?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Financial concept - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="What is qualified investor?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Definition question - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="How to invest in funds?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="How-to question - informational",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="Obrigado",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Portuguese gratitude",
        tier=4, category="closing"
    ),
    EvalQuery(
        query="Oi",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Portuguese greeting",
        tier=4, category="greeting"
    ),
    EvalQuery(
        query="O que é um fundo de investimento?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Portuguese definition question",
        tier=4, category="informational"
    ),
    EvalQuery(
        query="Como funciona tributação de fundos?",
        expected_intents=["informational"],
        expected_extraction={},
        expected_response_type="no_results",
        evaluation_type="response_type_match",
        why_tricky="Portuguese tax question - informational",
        tier=4, category="informational"
    ),
]
queries.extend(edge_conversational)

# --- 4.4 CONTEXT-DEPENDENT FOLLOWUPS (30 queries) ---
# These require conversation history to interpret correctly
edge_followup = [
    EvalQuery(
        query="Show me more",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="response_type_match",
        why_tricky="Pagination request - needs context",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Itau equity funds\nAgent: Here are 50 Itau equity funds..."
    ),
    EvalQuery(
        query="Next 10",
        expected_intents=["general_browse", "has_numeric_filter"],
        expected_extraction={"numeric_filter": {"top_n": 10}},
        expected_response_type="list_results",
        evaluation_type="response_type_match",
        why_tricky="Pagination with count - needs context",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: FII funds\nAgent: Here are the first 10 FIIs..."
    ),
    EvalQuery(
        query="Only from Itau",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Itau"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Refinement - filter previous results",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Equity funds\nAgent: Here are 100 equity funds..."
    ),
    EvalQuery(
        query="Remove multimarket",
        expected_intents=["find_by_criteria"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="response_type_match",
        why_tricky="Negative refinement",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Itau funds\nAgent: Here are Itau funds across classes..."
    ),
    EvalQuery(
        query="What about Vale?",
        expected_intents=["find_by_exposure"],
        expected_extraction={"asset_name": ["Vale"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Topic shift to exposure",
        tier=4, category="followup",
        expected_context_status="reset",
        history_context="User: Funds holding Petrobras\nAgent: Here are funds with Petrobras..."
    ),
    EvalQuery(
        query="Top 5",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"operator": "top", "top_n": 5}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Ranking on previous results",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Equity funds\nAgent: Here are 100 equity funds..."
    ),
    EvalQuery(
        query="Cheaper ones",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "management_fee", "operator": "min"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Comparative refinement",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Fixed income funds\nAgent: Here are fixed income funds..."
    ),
    EvalQuery(
        query="Better performing",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "return", "operator": "top"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Performance refinement",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Multimarket funds\nAgent: Here are multimarket funds..."
    ),
    EvalQuery(
        query="And FIP too",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FIP"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Addition to previous criteria",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: FII funds\nAgent: Here are FII funds..."
    ),
    EvalQuery(
        query="Now Bradesco",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Manager switch - should reset",
        tier=4, category="followup",
        expected_context_status="reset",
        history_context="User: Itau funds\nAgent: Here are Itau funds..."
    ),
    EvalQuery(
        query="Actually, I want fixed income",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Topic change - should reset",
        tier=4, category="followup",
        expected_context_status="reset",
        history_context="User: Equity funds\nAgent: Here are equity funds..."
    ),
    EvalQuery(
        query="Which has highest fee?",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "management_fee", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Question about previous results",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: BTG multimarket\nAgent: Here are 10 BTG multimarket funds..."
    ),
    EvalQuery(
        query="Show me the first one",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="single_match",
        evaluation_type="response_type_match",
        why_tricky="Select from previous results",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Alaska Black\nAgent: Here are 3 Alaska Black funds..."
    ),
    EvalQuery(
        query="Compare them",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="response_type_match",
        why_tricky="Comparison request",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Top 5 FIIs\nAgent: Here are top 5 FIIs..."
    ),
    EvalQuery(
        query="Larger ones",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Size refinement",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Kinea FIIs\nAgent: Here are Kinea FIIs..."
    ),
    EvalQuery(
        query="With more investors",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "holders", "operator": "max"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Holders refinement",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Retail funds\nAgent: Here are retail funds..."
    ),
    EvalQuery(
        query="What do you recommend?",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Recommendation request - needs clarification",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Fixed income funds\nAgent: Here are fixed income funds..."
    ),
    EvalQuery(
        query="Details please",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="single_match",
        evaluation_type="response_type_match",
        why_tricky="Detail request on previous result",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Verde Scena\nAgent: Found Verde Scena FIM..."
    ),
    EvalQuery(
        query="Different manager",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Vague change request",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Itau equity\nAgent: Here are Itau equity funds..."
    ),
    EvalQuery(
        query="Different class",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="followup",
        evaluation_type="response_type_match",
        why_tricky="Vague change request",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Bradesco fixed income\nAgent: Here are Bradesco fixed income funds..."
    ),
    EvalQuery(
        query="Only qualified",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["QUALIFIED"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Audience refinement",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: XP multimarket\nAgent: Here are XP multimarket funds..."
    ),
    EvalQuery(
        query="For retail",
        expected_intents=["find_by_criteria"],
        expected_extraction={"target_audience": ["RETAIL"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Audience filter addition",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: FII funds\nAgent: Here are FII funds..."
    ),
    EvalQuery(
        query="With long term tax",
        expected_intents=["find_by_criteria"],
        expected_extraction={"has_long_term_taxation": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Boolean filter addition",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Fixed income funds\nAgent: Here are fixed income funds..."
    ),
    EvalQuery(
        query="Exclusive only",
        expected_intents=["find_by_criteria"],
        expected_extraction={"is_exclusive_fund": True},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Exclusive filter addition",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: BTG funds\nAgent: Here are BTG funds..."
    ),
    EvalQuery(
        query="mais fundos",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="response_type_match",
        why_tricky="Portuguese: more funds",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: Fundos de ações\nAgent: Aqui estão fundos de ações..."
    ),
    EvalQuery(
        query="E da Bradesco?",
        expected_intents=["find_by_criteria"],
        expected_extraction={"service_provider_entity": ["Bradesco"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese: And from Bradesco?",
        tier=4, category="followup",
        expected_context_status="reset",
        history_context="User: Fundos Itau\nAgent: Aqui estão fundos Itau..."
    ),
    EvalQuery(
        query="Agora renda fixa",
        expected_intents=["find_by_criteria"],
        expected_extraction={"investment_class": ["Renda Fixa"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese: Now fixed income",
        tier=4, category="followup",
        expected_context_status="reset",
        history_context="User: Fundos de ações BTG\nAgent: Aqui estão fundos de ações BTG..."
    ),
    EvalQuery(
        query="Somente FII",
        expected_intents=["find_by_criteria"],
        expected_extraction={"fund_type": ["FII"]},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese: Only FII",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Kinea funds\nAgent: Here are Kinea funds..."
    ),
    EvalQuery(
        query="Pode repetir?",
        expected_intents=["general_browse"],
        expected_extraction={},
        expected_response_type="list_results",
        evaluation_type="response_type_match",
        why_tricky="Portuguese: Can you repeat?",
        tier=4, category="followup",
        expected_context_status="keep",
        history_context="User: Verde funds\nAgent: Here are Verde funds..."
    ),
    EvalQuery(
        query="Os menores",
        expected_intents=["has_numeric_filter"],
        expected_extraction={"numeric_filter": {"metric": "aum", "operator": "min"}},
        expected_response_type="list_results",
        evaluation_type="extraction_match",
        why_tricky="Portuguese: The smallest",
        tier=4, category="followup",
        expected_context_status="refine_result_set",
        history_context="User: FIIs Kinea\nAgent: Aqui estão FIIs Kinea..."
    ),
]
queries.extend(edge_followup)

# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def generate_jsonl():
    """Generate JSONL file for evaluation"""
    output = []
    for i, q in enumerate(queries):
        record = {
            "id": i + 1,
            "query": q.query,
            "expected_intents": q.expected_intents,
            "expected_extraction": q.expected_extraction,
            "expected_response_type": q.expected_response_type,
            "evaluation_type": q.evaluation_type,
            "why_tricky": q.why_tricky,
            "tier": q.tier,
            "category": q.category,
        }
        
        # Add optional fields if present
        if q.expected_search_query_contains:
            record["expected_search_query_contains"] = q.expected_search_query_contains
        if q.expected_required_name_terms:
            record["expected_required_name_terms"] = q.expected_required_name_terms
        if q.expected_ambiguous is not None:
            record["expected_ambiguous"] = q.expected_ambiguous
        if q.expected_context_status:
            record["expected_context_status"] = q.expected_context_status
        if q.expected_language:
            record["expected_language"] = q.expected_language
        if q.history_context:
            record["history_context"] = q.history_context
            
        output.append(record)
    
    return output

def print_stats():
    """Print dataset statistics"""
    tier_counts = {}
    category_counts = {}
    eval_type_counts = {}
    
    for q in queries:
        tier_counts[q.tier] = tier_counts.get(q.tier, 0) + 1
        category_counts[q.category] = category_counts.get(q.category, 0) + 1
        eval_type_counts[q.evaluation_type] = eval_type_counts.get(q.evaluation_type, 0) + 1
    
    print(f"\n{'='*60}")
    print(f"FUND SEARCH EVALUATION DATASET STATISTICS")
    print(f"{'='*60}")
    print(f"\nTotal Queries: {len(queries)}")
    
    print(f"\nBy Tier:")
    for tier in sorted(tier_counts.keys()):
        print(f"  Tier {tier}: {tier_counts[tier]} queries")
    
    print(f"\nBy Category:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    print(f"\nBy Evaluation Type:")
    for eval_type, count in sorted(eval_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {eval_type}: {count}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    # Print statistics
    print_stats()
    
    # Generate JSONL
    data = generate_jsonl()
    
    # Write to file
    output_file = "src/evaluation/data/fund_search_evaluation.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"\nGenerated {len(data)} queries to {output_file}")

