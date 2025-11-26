"""
Known Brazilian Investment Funds - Ground Truth Reference
==========================================================
This file contains verified fund information for evaluation testing.
CNPJs and fund details sourced from CVM (Brazilian SEC) public data.

These can be used to verify that:
1. Name searches return the correct CNPJ
2. Manager searches include the expected funds
3. Criteria filters return appropriate results
"""

# Famous Brazilian Funds - Name → CNPJ mapping
KNOWN_FUNDS = {
    # Alaska Asset Management
    "alaska_black_institucional": {
        "cnpj": "23.517.757/0001-34",
        "name": "ALASKA BLACK INSTITUCIONAL FIA",
        "manager": "Alaska",
        "investment_class": "Ações",
        "fund_type": "FI",
    },
    "alaska_black_fic": {
        "cnpj": "28.443.404/0001-10",
        "name": "ALASKA BLACK FIC FIA II BDR NÍVEL I",
        "manager": "Alaska",
        "investment_class": "Ações",
        "fund_type": "FIF",
    },
    
    # Verde Asset Management
    "verde_scena": {
        "cnpj": "35.688.927/0001-74",
        "name": "VERDE SCENA ADVISORY FIC FIM",
        "manager": "Verde",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    "verde_am_70": {
        "cnpj": "04.892.108/0001-06",
        "name": "VERDE AM 70 FICFI MULTIMERCADO",
        "manager": "Verde",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Dynamo
    "dynamo_cougar": {
        "cnpj": "73.232.530/0001-39",
        "name": "DYNAMO COUGAR FUNDO DE INVESTIMENTO EM AÇÕES",
        "manager": "Dynamo",
        "investment_class": "Ações",
        "fund_type": "FI",
    },
    
    # SPX Capital
    "spx_nimitz": {
        "cnpj": "23.243.147/0001-55",
        "name": "SPX NIMITZ FEEDER FIC FIM",
        "manager": "SPX",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    "spx_raptor": {
        "cnpj": "23.073.499/0001-20",
        "name": "SPX RAPTOR FEEDER FIC FIM",
        "manager": "SPX",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Kapitalo
    "kapitalo_kappa": {
        "cnpj": "25.068.790/0001-08",
        "name": "KAPITALO KAPPA FIN FIC FIM",
        "manager": "Kapitalo",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    "kapitalo_zeta": {
        "cnpj": "29.754.678/0001-00",
        "name": "KAPITALO ZETA FIC FIM",
        "manager": "Kapitalo",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Ibiuna
    "ibiuna_hedge": {
        "cnpj": "11.017.946/0001-26",
        "name": "IBIUNA HEDGE STH FIC FIM",
        "manager": "Ibiuna",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Occam
    "occam_retorno_absoluto": {
        "cnpj": "14.609.319/0001-17",
        "name": "OCCAM RETORNO ABSOLUTO FIC FIM",
        "manager": "Occam",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # JGP
    "jgp_strategy": {
        "cnpj": "11.225.860/0001-02",
        "name": "JGP STRATEGY FIC FIM",
        "manager": "JGP",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Legacy Capital
    "legacy_capital": {
        "cnpj": "29.679.575/0001-33",
        "name": "LEGACY CAPITAL FIC FIM",
        "manager": "Legacy Capital",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Absoluto Partners
    "absoluto_partners": {
        "cnpj": "14.525.065/0001-82",
        "name": "ABSOLUTO PARTNERS FIC FIM",
        "manager": "Absoluto Partners",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Constellation
    "constellation_compounders": {
        "cnpj": "29.516.363/0001-75",
        "name": "CONSTELLATION COMPOUNDERS FIC FIA BDR NÍVEL I",
        "manager": "Constellation",
        "investment_class": "Ações",
        "fund_type": "FIF",
    },
    
    # Adam Capital
    "adam_macro": {
        "cnpj": "26.660.809/0001-45",
        "name": "ADAM MACRO II FIC FIM",
        "manager": "Adam Capital",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Truxt
    "truxt_long_short": {
        "cnpj": "23.861.310/0001-00",
        "name": "TRUXT LONG SHORT FIC FIM",
        "manager": "Truxt",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Giant Steps
    "giant_steps_horizon": {
        "cnpj": "22.227.389/0001-12",
        "name": "GIANT STEPS HORIZON FIC FIM",
        "manager": "Giant Steps",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Moat Capital
    "moat_capital": {
        "cnpj": "22.876.575/0001-60",
        "name": "MOAT CAPITAL FIC FIA",
        "manager": "Moat Capital",
        "investment_class": "Ações",
        "fund_type": "FIF",
    },
    
    # Bahia Asset
    "bahia_long_short": {
        "cnpj": "14.107.426/0001-10",
        "name": "BAHIA AM LONG SHORT FIC FIM",
        "manager": "Bahia Asset",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
    
    # Ace Capital
    "ace_capital_fia": {
        "cnpj": "28.025.676/0001-06",
        "name": "ACE CAPITAL FIA",
        "manager": "Ace Capital",
        "investment_class": "Ações",
        "fund_type": "FI",
    },
    
    # Brasil Capital
    "brasil_capital": {
        "cnpj": "19.077.409/0001-71",
        "name": "BRASIL CAPITAL 30 FIC FIA",
        "manager": "Brasil Capital",
        "investment_class": "Ações",
        "fund_type": "FIF",
    },
    
    # Kinea (FIIs)
    "kinea_renda_imobiliaria": {
        "cnpj": "12.005.956/0001-65",
        "name": "KINEA RENDA IMOBILIÁRIA FII",
        "manager": "Kinea",
        "investment_class": "FII",
        "fund_type": "FII",
        "ticker": "KNRI11",
    },
    "kinea_indices_precos": {
        "cnpj": "24.960.430/0001-13",
        "name": "KINEA ÍNDICES DE PREÇOS FII",
        "manager": "Kinea",
        "investment_class": "FII",
        "fund_type": "FII",
        "ticker": "KNIP11",
    },
    
    # BTG Pactual (FIIs)
    "btg_logistica": {
        "cnpj": "11.839.593/0001-09",
        "name": "BTG PACTUAL LOGÍSTICA FII",
        "manager": "BTG Pactual",
        "investment_class": "FII",
        "fund_type": "FII",
        "ticker": "BTLG11",
    },
    
    # XP (FIIs)
    "xp_malls": {
        "cnpj": "28.757.546/0001-00",
        "name": "XP MALLS FII",
        "manager": "XP",
        "investment_class": "FII",
        "fund_type": "FII",
        "ticker": "XPML11",
    },
    
    # Vinci Partners (FIP)
    "vinci_infra": {
        "cnpj": "29.717.804/0001-93",
        "name": "VINCI INFRA FIP-IE",
        "manager": "Vinci Partners",
        "investment_class": "FIP",
        "fund_type": "FIP",
    },
    
    # Patria Investimentos
    "patria_infra_core": {
        "cnpj": "37.521.238/0001-73",
        "name": "PATRIA INFRAESTRUTURA CORE FIP-IE",
        "manager": "Patria",
        "investment_class": "FIP",
        "fund_type": "FIP",
    },
    
    # Opportunity
    "opportunity_total": {
        "cnpj": "04.206.024/0001-02",
        "name": "OPPORTUNITY TOTAL FIC FIM",
        "manager": "Opportunity",
        "investment_class": "Multimercado",
        "fund_type": "FIF",
    },
}

# Manager → Expected Fund CNPJs (for manager search validation)
MANAGER_FUNDS = {
    "itau": [
        "03.660.879/0001-96",  # ITAÚ AÇÕES IBOVESPA ATIVO
        "01.585.137/0001-06",  # ITAÚ INDEX AÇÕES IBOVESPA
        "05.266.009/0001-90",  # ITAÚ MULTIMERCADO
    ],
    "bradesco": [
        "01.536.539/0001-03",  # BRADESCO FIA
        "73.958.485/0001-06",  # BRADESCO PRIME FIC FI
        "04.836.562/0001-04",  # BRADESCO H MULTIMERCADO
    ],
    "btg": [
        "10.320.188/0001-02",  # BTG PACTUAL ABSOLUTE RETURN
        "17.044.692/0001-35",  # BTG PACTUAL DISCOVERY
    ],
    "xp": [
        "18.116.141/0001-18",  # XP SELECTION FIC FIM
        "12.283.970/0001-60",  # XP MACRO FIM
    ],
    "kinea": [
        "09.456.451/0001-55",  # KINEA MULTIMERCADO
        "12.005.956/0001-65",  # KINEA RENDA IMOBILIÁRIA FII
    ],
}

# Fund Type → Sample CNPJs (for filter validation)
FUND_TYPE_SAMPLES = {
    "FII": [
        "12.005.956/0001-65",  # KINEA RENDA IMOBILIÁRIA
        "11.839.593/0001-09",  # BTG PACTUAL LOGÍSTICA
        "28.757.546/0001-00",  # XP MALLS
        "97.521.225/0001-25",  # IRIDIUM RECEBÍVEIS FII
    ],
    "FIP": [
        "29.717.804/0001-93",  # VINCI INFRA FIP-IE
        "37.521.238/0001-73",  # PATRIA INFRAESTRUTURA CORE
        "14.534.011/0001-97",  # BTG PACTUAL INFRAESTRUTURA I
    ],
    "ETF": [
        "19.909.560/0001-91",  # BOVA11 - iShares Ibovespa
        "36.588.217/0001-01",  # IVVB11 - iShares S&P 500
        "18.055.799/0001-44",  # SMAL11 - iShares Small Cap
    ],
    "FIDC": [
        "07.677.256/0001-10",  # EMPIRICA FIDC
        "11.171.628/0001-55",  # RB CAPITAL FIDC
    ],
}

# Investment Class → Sample CNPJs
INVESTMENT_CLASS_SAMPLES = {
    "Ações": [
        "73.232.530/0001-39",  # DYNAMO COUGAR
        "23.517.757/0001-34",  # ALASKA BLACK INSTITUCIONAL
        "29.516.363/0001-75",  # CONSTELLATION COMPOUNDERS
    ],
    "Multimercado": [
        "35.688.927/0001-74",  # VERDE SCENA
        "23.243.147/0001-55",  # SPX NIMITZ
        "25.068.790/0001-08",  # KAPITALO KAPPA
    ],
    "Renda Fixa": [
        "00.068.305/0001-35",  # ARX TARGET FI RF
        "03.737.206/0001-97",  # ITAÚ RF SIMPLES
    ],
}

# Target Audience → Sample CNPJs  
TARGET_AUDIENCE_SAMPLES = {
    "QUALIFIED": [
        "35.688.927/0001-74",  # VERDE SCENA (qualified)
        "23.243.147/0001-55",  # SPX NIMITZ (qualified)
    ],
    "PROFESSIONAL": [
        "04.892.108/0001-06",  # VERDE AM 70 (professional)
    ],
    "RETAIL": [
        "19.909.560/0001-91",  # BOVA11 (retail)
        "03.737.206/0001-97",  # ITAÚ RF SIMPLES (retail)
    ],
}

def get_fund_cnpj(fund_key: str) -> str | None:
    """Get CNPJ for a known fund by key"""
    fund = KNOWN_FUNDS.get(fund_key)
    return fund["cnpj"] if fund else None

def get_funds_by_manager(manager: str) -> list[str]:
    """Get list of CNPJs for funds managed by given manager"""
    manager_lower = manager.lower()
    
    # Check direct mapping
    if manager_lower in MANAGER_FUNDS:
        return MANAGER_FUNDS[manager_lower]
    
    # Check KNOWN_FUNDS
    cnpjs = []
    for fund in KNOWN_FUNDS.values():
        if fund["manager"].lower() == manager_lower:
            cnpjs.append(fund["cnpj"])
    
    return cnpjs

def get_funds_by_type(fund_type: str) -> list[str]:
    """Get sample CNPJs for a fund type"""
    return FUND_TYPE_SAMPLES.get(fund_type, [])

def get_funds_by_class(investment_class: str) -> list[str]:
    """Get sample CNPJs for an investment class"""
    return INVESTMENT_CLASS_SAMPLES.get(investment_class, [])

# Export for use in tests
__all__ = [
    "KNOWN_FUNDS",
    "MANAGER_FUNDS", 
    "FUND_TYPE_SAMPLES",
    "INVESTMENT_CLASS_SAMPLES",
    "TARGET_AUDIENCE_SAMPLES",
    "get_fund_cnpj",
    "get_funds_by_manager",
    "get_funds_by_type",
    "get_funds_by_class",
]

