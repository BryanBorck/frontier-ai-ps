"""Fast regex-based parser for common query patterns.

This parser handles simple, common queries using regex patterns instead of LLM calls.
Falls back to LLM for complex queries.
"""

import re

from .module_pipeline import FundSearchCriteria

# Company name patterns (case-insensitive)
COMPANY_PATTERNS = {
    # Banks and Major Platforms
    r"\b(ita[uú])\b": "itau",
    r"\b(bradesco|bram)\b": "bradesco",
    r"\b(santander)\b": "santander",
    r"\b(xp)\b": "xp",
    r"\b(btg(?:\s+pactual)?)\b": "btg",
    r"\b(banco\s+do\s+brasil|bb)\b": "banco do brasil",
    r"\b(safra)\b": "safra",
    r"\b(credit\s+suisse|cshg)\b": "credit suisse",
    r"\b(bny(?:\s+mellon)?)\b": "bny mellon",
    r"\b(daycoval)\b": "daycoval",
    r"\b(citibank|citi)\b": "citibank",
    r"\b(bnp(?:\s+paribas)?)\b": "bnp paribas",
    # Top Independent Asset Managers
    r"\b(vinci)\b": "vinci",
    r"\b(arx)\b": "arx",
    r"\b(kinea)\b": "kinea",
    r"\b(spx)\b": "spx",
    r"\b(jgp)\b": "jgp",
    r"\b(adam)\b": "adam",
    r"\b(kapitalo)\b": "kapitalo",
    r"\b(g[aá]vea)\b": "gavea",
    r"\b(verde)\b": "verde",
    r"\b(occam)\b": "occam",
    r"\b(truxt)\b": "truxt",
    r"\b(pátria|patria)\b": "patria",
    r"\b(absoluto)\b": "absoluto",
    r"\b(bahia)\b": "bahia",
    r"\b(ip(?:\s+capital)?)\b": "ip capital",
    r"\b(dynamo)\b": "dynamo",
    r"\b(constellation)\b": "constellation",
    r"\b(bogari)\b": "bogari",
    r"\b(valet)\b": "valet",
    r"\b(navi)\b": "navi",
    r"\b(jpmorgan|jp\s+morgan)\b": "jpmorgan",
    r"\b(votorantim|bv)\b": "votorantim",
    r"\b([óo]rama)\b": "orama",
}

# Mapping from internal company name to standardized service provider entity
SERVICE_PROVIDER_MAPPING = {
    "banco do brasil": "BB",
    "bny mellon": "BNY",
    "citibank": "CITI",
    "bnp paribas": "BNP",
    "ip capital": "IP",
}

# Fund type patterns (exact matches)
# Ordered by frequency in database (most common first)
FUND_TYPE_PATTERNS = {
    # Most common types - need negative lookahead to avoid matching prefixes
    r"\b(fi)(?![-\w])": "FI",  # Match FI but not FI-FGTS, FIDC, etc.
    r"\b(fip)(?![-\w])": "FIP",
    r"\b(fif)(?![-\w])": "FIF",
    r"\b(fidc)(?![-\w])": "FIDC",
    r"\b(fii)(?![-\w])": "FII",
    # Compound types with hyphens (check these before base types)
    r"\b(fi-fgts)\b": "FI-FGTS",
    r"\b(fic-fitvm)\b": "FIC-FITVM",
    r"\b(fmp-fgts\s+cl)\b": "FMP-FGTS CL",
    r"\b(fmp-fgts)\b": "FMP-FGTS",
    r"\b(fmia-cl)\b": "FMIA-CL",
    r"\b(fcce-ai)\b": "FCCE-AI",
    r"\b(fiq-fmia)\b": "FIQ-FMIA",
    # Other fund types (alphabetically)
    r"\b(facfif)\b": "FACFIF",
    r"\b(fapi)\b": "FAPI",
    r"\b(fcce)\b": "FCCE",
    r"\b(ficart)\b": "FICART",
    r"\b(fice)\b": "FICE",
    r"\b(fiex)\b": "FIEX",
    r"\b(fifdiv)\b": "FIFDIV",
    r"\b(fiim)\b": "FIIM",
    r"\b(fitvm)\b": "FITVM",
    r"\b(fmai)\b": "FMAI",
    r"\b(fmia)\b": "FMIA",
    r"\b(fmiee)\b": "FMIEE",
    r"\b(fpce)\b": "FPCE",
    r"\b(fpds)\b": "FPDS",
    r"\b(funcine)\b": "FUNCINE",
    # ETF (not in DB but common in queries)
    # r"\b(etf)\b": "ETF",
}

# Investment class patterns
# Ordered by frequency in database (most common first)
INVESTMENT_CLASS_PATTERNS = {
    # Most common classes
    r"\b(multimercado)\b": "Multimercado",
    r"\b(a[cç][oõ]es)\b": "Ações",
    r"\b(renda\s+fixa)\b": "Renda Fixa",
    r"\b(referenciado)\b": "Referenciado",
    r"\b(cambial)\b": "Cambial",
    r"\b(curto\s+prazo)\b": "Curto Prazo",
    # Compound classes with spaces/hyphens
    r"\b(d[ií]vida\s+externa)\b": "Dívida Externa",
    r"\b(cr[eé]dito\s+privado)\b": "Crédito Privado",
    r"\b(fic\s+fidc)\b": "FIC FIDC",
    r"\b(fic\s+fip)\b": "FIC FIP",
    # FIDC variants
    r"\b(ficfidc-np)\b": "FICFIDC-NP",
    r"\b(fidc-pips)\b": "FIDC-PIPS",
    r"\b(fidc-np)\b": "FIDC-NP",
    r"\b(fidcfiagro)\b": "FIDCFIAGRO",
    r"\b(fidc)(?![-\w])": "FIDC",
    # FII variants
    r"\b(fii-fiagro)\b": "FII-FIAGRO",
    r"\b(fii)(?![-\w])": "FII",
    # FIP variants
    r"\b(fip\s+multi)\b": "FIP Multi",
    r"\b(fip\s+ie)\b": "FIP IE",
    r"\b(fip\s+cs)\b": "FIP CS",
    r"\b(fip\s+ee)\b": "FIP EE",
    r"\b(fip\s+pd&i)\b": "FIP PD&I",
    r"\b(fip-fiagro)\b": "FIP-FIAGRO",
    r"\b(fip)(?![-\w\s])": "FIP",
    # Other classes
    r"\b(fmp-fgts)\b": "FMP-FGTS",
    r"\b(fmiee)\b": "FMIEE",
    r"\b(funcine)\b": "FUNCINE",
}


def fast_parse(query: str) -> FundSearchCriteria | None:
    """Try to parse query using regex patterns.

    Returns FundSearchCriteria if pattern matches, None otherwise.
    This is ~1000x faster than LLM parsing for simple queries.

    Args:
        query: User's natural language query

    Returns:
        FundSearchCriteria if simple pattern matched, None if needs LLM
    """
    query_lower = query.lower()

    # Extract company name and service provider
    fund_legal_name = None
    service_provider_entity = None
    for pattern, company in COMPANY_PATTERNS.items():
        if re.search(pattern, query_lower):
            fund_legal_name = company
            # Map to standardized service provider entity
            if company in SERVICE_PROVIDER_MAPPING:
                service_provider_entity = SERVICE_PROVIDER_MAPPING[company]
            else:
                service_provider_entity = company.upper()
            break

    # Extract fund type
    fund_type = None
    for pattern, ftype in FUND_TYPE_PATTERNS.items():
        if re.search(pattern, query_lower):
            fund_type = ftype
            break

    # Extract investment class
    investment_class = None
    for pattern, iclass in INVESTMENT_CLASS_PATTERNS.items():
        if re.search(pattern, query_lower):
            investment_class = iclass
            break

    # Extract boolean and enum filters
    fund_of_funds = None
    if re.search(r"\b(fund\s+of\s+funds|fof|fundo\s+de\s+fundos)\b", query_lower):
        fund_of_funds = True

    is_exclusive_fund = None
    if re.search(r"\b(exclusive?|exclusiv[oa])\b", query_lower):
        is_exclusive_fund = True

    target_audience = None
    if re.search(r"\b(qualified\s+investors?|investidores?\s+qualificados?)\b", query_lower):
        target_audience = "QUALIFIED"
    elif re.search(r"\b(professional\s+investors?|investidores?\s+profissionais?)\b", query_lower):
        target_audience = "PROFESSIONAL"
    elif re.search(r"\b(retail\s+investors?|investidores?\s+de\s+varejo)\b", query_lower):
        target_audience = "RETAIL"

    manager_type = None
    if re.search(r"\b(corporate\s+manage[dr]|gest[ãa]o\s+corporativa)\b", query_lower):
        manager_type = "CORPORATE"
    elif re.search(r"\b(individual\s+manage[dr]|gest[ãa]o\s+individual)\b", query_lower):
        manager_type = "INDIVIDUAL"

    can_invest_abroad = None
    if re.search(
        r"\b(invest\s+abroad|international\s+invest|investimento\s+no\s+exterior)\b",
        query_lower,
    ):
        can_invest_abroad = True

    has_long_term_taxation = None
    if re.search(r"\b(long[- ]?term\s+tax|tributa[cç][ãa]o\s+de\s+longo\s+prazo)\b", query_lower):
        has_long_term_taxation = True

    # If we found at least one criterion, return it
    if (
        fund_legal_name
        or service_provider_entity
        or fund_type
        or investment_class
        or fund_of_funds
        or is_exclusive_fund
        or target_audience
        or manager_type
        or can_invest_abroad
        or has_long_term_taxation
    ):
        return FundSearchCriteria(
            fund_legal_name=fund_legal_name,
            service_provider_entity=service_provider_entity,
            fund_type=fund_type,
            investment_class=investment_class,
            fund_of_funds=fund_of_funds,
            target_audience=target_audience,
            manager_type=manager_type,
            is_exclusive_fund=is_exclusive_fund,
            can_invest_abroad_100_pct=can_invest_abroad,
            has_long_term_taxation=has_long_term_taxation,
        )

    # No simple pattern matched - needs LLM
    return None


def can_fast_parse(query: str) -> bool:
    """Check if query can be parsed with regex (fast path).

    Args:
        query: User's natural language query

    Returns:
        True if query matches simple patterns, False if needs LLM
    """
    return fast_parse(query) is not None
