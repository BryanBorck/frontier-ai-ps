from typing import Literal

import dspy

from src.agent.fund_search.models.fund import FundResult
from src.agent.response.signatures.response import ResponseSignature


class ResponseGenerator(dspy.Module):
    """
    Module for generating natural language responses from search results.
    """

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(ResponseSignature)

    def forward(
        self,
        query: str,
        results: list[FundResult],
        response_type: Literal[
            "single_match",
            "list_results",
            "disambiguation",
            "no_results",
            "too_many_results",
            "informational",
        ],
        user_language: Literal["pt", "en"] = "pt",
        interpretation_note: str | None = None,
    ) -> dspy.Prediction:
        """
        Generate a response based on results and response type.
        """
        # Create a summary string of the results for the LLM
        results_summary = self._format_results_summary(results)

        result = self.generate(
            query=query,
            results_summary=results_summary,
            response_type=response_type,
            interpretation_note=interpretation_note,
            user_language=user_language,
        )

        return dspy.Prediction(answer=result.answer)

    def _format_results_summary(self, results: list[FundResult]) -> str:
        """Format results into a concise text summary for context."""
        if not results:
            return "No results found."

        summary = f"Found {len(results)} results.\n"

        for i, item in enumerate(results[:20]):  # Limit context window usage
            summary += f"{i + 1}. {item.legal_name} (CNPJ: {item.cnpj})\n"
            if item.investment_class:
                summary += f"   Class: {item.investment_class}\n"
            if item.aum:
                summary += f"   AUM: {item.aum}\n"
            if item.description:
                summary += f"   Description: {item.description}\n"
            summary += "\n"

        return summary
