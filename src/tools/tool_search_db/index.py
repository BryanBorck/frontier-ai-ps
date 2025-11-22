"""Tool: Search Database

Search for Brazilian investment funds in the database using structured criteria.
Returns structured fund data including legal name, CNPJ, type, and investment class.
"""

from src.tools.tool_parse_query.module_pipeline import FundSearchCriteria

from .module_pipeline import FundResult, execute, search_funds


def tool_search_db(input_data: dict) -> list[dict]:
    """Main tool entry point for searching funds in the database.

    Input schema (from schema.json):
        {
          "criteria": {
            "fund_legal_name": string | null,
            "fund_type": string | null,
            "investment_class": string | null,
            "fund_of_funds": boolean | null
          },
          "limit": integer (default: 10)
        }

    Output schema (from schema.json):
        [
          {
            "legal_name": string,
            "cnpj": string,
            "fund_type": string | null,
            "investment_class": string | null
          }
        ]

    Args:
        input_data: Dictionary with 'criteria' and optional 'limit' keys

    Returns:
        List of dictionaries with fund metadata

    Raises:
        ValueError: If 'criteria' field is missing
    """
    criteria = input_data.get("criteria")
    if criteria is None:
        raise ValueError("Missing required field 'criteria'")

    limit = input_data.get("limit", 10)

    return execute(criteria=criteria, limit=limit)


class _FundSearchInternal:
    """Internal search function for ReAct agent compatibility.

    This class is not part of the public tool API.
    Use tool_search_db() for the standard tool interface.
    """

    def search(self, criteria: FundSearchCriteria, limit: int = 10) -> list[FundResult]:
        """Search for funds and return FundResult objects.

        Args:
            criteria: FundSearchCriteria object with search parameters
            limit: Maximum number of results to return

        Returns:
            List of FundResult objects
        """
        return search_funds(criteria, limit=limit)


# Export only the main tool function
__all__ = ["tool_search_db"]
