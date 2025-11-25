from typing import Literal

import dspy

from src.agent.models.fund import SearchResultItem
from src.agent.signatures.response import GenerateResponseSignature


class ResponseGenerator(dspy.Module):
    """
    Module for generating natural language responses from search results.
    """

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(GenerateResponseSignature)

    def forward(
        self,
        query: str,
        results: list[SearchResultItem],
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

        Args:
            interpretation_note: If provided, the query was potentially ambiguous.
                                 Response should include follow-up asking about alternatives.
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

    def _format_results_summary(self, results: list[SearchResultItem]) -> str:
        """Format results into a concise text summary for context."""
        if not results:
            return "No results found."

        summary = f"Found {len(results)} results.\n"

        for i, item in enumerate(results[:20]):  # Limit context window usage
            summary += f"{i + 1}. {item.legal_name} (CNPJ: {item.cnpj})\n"
            summary += f"   Source: {item.source} | Score: {item.combined_score:.2f}\n"
            if item.fund_details:
                if item.fund_details.investment_class:
                    summary += f"   Class: {item.fund_details.investment_class}\n"
                if item.fund_details.aum:
                    summary += f"   AUM: {item.fund_details.aum}\n"
                if item.fund_details.description:
                    summary += f"   Description: {item.fund_details.description}\n"
            summary += "\n"

        return summary
