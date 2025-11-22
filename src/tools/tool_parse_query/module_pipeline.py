"""DSPy module pipeline for parsing fund queries."""

from enum import Enum

import dspy
from pydantic import BaseModel, Field


class TargetAudience(str, Enum):
    """Target audience for the fund."""

    PROFESSIONAL = "PROFESSIONAL"
    QUALIFIED = "QUALIFIED"
    RETAIL = "RETAIL"


class ManagerType(str, Enum):
    """Fund manager type."""

    CORPORATE = "CORPORATE"
    INDIVIDUAL = "INDIVIDUAL"


class FundSearchCriteria(BaseModel):
    """Structured search criteria extracted from user query."""

    fund_legal_name: str | None = Field(
        None,
        description=(
            "Company or brand name to search in fund's legal name. "
            "Extract any company/brand names like BTG, Bradesco, Itaú, Vinci, etc. "
            "This is for partial text matching in the fund name, NOT for fund types or investment classes."
        ),
    )
    service_provider_entity: str | None = Field(
        None,
        description=(
            "The standardized entity name for the service provider (Manager, Administrator, Custodian). "
            "Should be one of: ITAU, BRADESCO, SANTANDER, BTG, XP, SAFRA, BB, BNY, CREDIT SUISSE, "
            "CITI, BNP, JPMORGAN, VINCI, KINEA, SPX, ARX, ADAM, GAVEA, VERDE, OCCAM, TRUXT, KAPITALO, "
            "JGP, PATRIA, ABSOLUTO, BAHIA, IP, DYNAMO, CONSTELLATION, BOGARI, VALET, NAVI, DAYCOVAL, "
            "VOTORANTIM, ABC, GENIAL, GUIDE, ORAMA, RICO, CLEAR, MODAL. "
            "Use this for more accurate entity matching than simple name search."
        ),
    )
    fund_type: str | None = Field(
        None,
        description=(
            "Fund type - ONLY use these specific values: FI, FIP, FIDC, FII, ETF, or 'CLASSES - FIF'. "
            "These are regulatory fund classifications, not company names or investment strategies."
        ),
    )
    investment_class: str | None = Field(
        None,
        description=(
            "Investment class/strategy - examples: Multimercado, Ações, Renda Fixa, Cambial, etc. "
            "These describe the investment strategy, not the company name or fund type."
        ),
    )
    fund_of_funds: bool | None = Field(
        None, description="Whether to filter for fund of funds - only if user explicitly specifies"
    )
    target_audience: TargetAudience | None = Field(
        None,
        description=(
            "Target audience for the fund. Values: PROFESSIONAL, QUALIFIED, RETAIL. "
            "Only set if user explicitly mentions qualified/professional/retail investors."
        ),
    )
    manager_type: ManagerType | None = Field(
        None,
        description=(
            "Fund manager type. Values: CORPORATE, INDIVIDUAL. "
            "Only set if user explicitly specifies corporate or individual management."
        ),
    )
    is_exclusive_fund: bool | None = Field(
        None,
        description="Whether to filter for exclusive funds - only if user explicitly specifies",
    )
    can_invest_abroad_100_pct: bool | None = Field(
        None,
        description="Whether fund can invest 100% abroad - only if user explicitly specifies",
    )
    has_long_term_taxation: bool | None = Field(
        None,
        description="Whether fund has long-term taxation benefits - only if user explicitly specifies",
    )


class ParseQuerySignature(dspy.Signature):
    """Parse user query to extract structured fund search criteria.

    Extract fund search parameters from natural language queries.

    Guidelines:
    - fund_legal_name: Extract company/brand names (BTG, Bradesco, Vinci, Itaú, etc.)
    - service_provider_entity: Extract standardized entity name (ITAU, BTG, XP, etc.) if a major institution is mentioned
    - fund_type: Extract ONLY these values: FI, FIP, FIDC, FII, ETF, or 'CLASSES - FIF'
    - investment_class: Extract investment strategies (Multimercado, Ações, Renda Fixa, etc.)
    - fund_of_funds: Set to True ONLY if user explicitly mentions "fund of funds" or "FoF"
    - target_audience: PROFESSIONAL, QUALIFIED, or RETAIL - only if explicitly mentioned
    - manager_type: CORPORATE or INDIVIDUAL - only if explicitly mentioned
    - is_exclusive_fund: Set to True ONLY if user explicitly mentions "exclusive"
    - can_invest_abroad_100_pct: Set to True ONLY if user mentions investing abroad/internationally
    - has_long_term_taxation: Set to True ONLY if user mentions long-term taxation benefits

    Examples:
    - "btg funds" → fund_legal_name="btg", service_provider_entity="BTG"
    - "bradesco funds" → fund_legal_name="bradesco", service_provider_entity="BRADESCO"
    - "find FIP funds" → fund_type="FIP"
    - "show me Multimercado funds" → investment_class="Multimercado"
    - "btg FIP funds" → fund_legal_name="btg", service_provider_entity="BTG", fund_type="FIP"
    - "fund of funds from itau" → fund_legal_name="itau", service_provider_entity="ITAU", fund_of_funds=True
    - "exclusive fund of bradesco" → fund_legal_name="bradesco", is_exclusive_fund=True
    - "fund for qualified investors" → target_audience="QUALIFIED"
    - "corporate managed fund" → manager_type="CORPORATE"
    """

    query: str = dspy.InputField(desc="User's natural language query about funds")
    criteria: FundSearchCriteria = dspy.OutputField(
        desc="Structured search criteria extracted from the query"
    )


class ParseQueryModule(dspy.Module):
    """DSPy module for parsing fund queries into structured criteria."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(ParseQuerySignature)

    def forward(self, query: str) -> FundSearchCriteria:
        """Parse the query and return structured criteria.

        Args:
            query: Natural language query from the user

        Returns:
            FundSearchCriteria with extracted parameters
        """
        result = self.predictor(query=query)
        return result.criteria


def execute(query: str) -> dict:
    """Execute the fund query parsing tool.

    Args:
        query: Natural language query from the user

    Returns:
        Dictionary with extracted fund search criteria
    """
    module = ParseQueryModule()
    criteria = module(query=query)
    return criteria.model_dump()
