import contextlib
import os
import shutil

import dspy

from src.agent.fund_details.tool import FundDetailsTool
from src.agent.fund_search.models.output import SearchOutput
from src.agent.fund_search.modules.intent import IntentClassifier
from src.agent.fund_search.orchestrator import FundSearchTool
from src.agent.response.generator import ResponseGenerator
from src.agent.web_search.tool import WebSearchTool


class MainAgent:
    """
    Main Agent Orchestrator.
    Combines FundSearchTool (Discovery) and FundDetailsTool (Retrieval).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
    ):
        self.lm = dspy.LM(model=f"openai/{model}", api_key=api_key)
        dspy.configure(lm=self.lm)

        # Components
        # MainAgent doesn't need to know about tracing config for FundSearchTool anymore if we rely on defaults
        # or if we want to pass specific config, we do it here.
        # User requested to remove tracing from MainAgent.

        self.search_tool = FundSearchTool(
            api_key=api_key,
            model=model,
            enable_mlflow=True,  # Enable tracing for fund search only
        )

        self.details_tool = FundDetailsTool()
        self.web_search_tool = WebSearchTool()
        self.response_generator = ResponseGenerator()

        # Classifier for MainAgent to decide flow
        self.intent_classifier = IntentClassifier()

        # State
        self.history = []

    def get_history(self) -> list[dict[str, str]]:
        """Return conversation history."""
        return self.history

    def reset_history(self):
        """Reset conversation history and clear LLM cache."""
        self.history = []
        self.search_tool.clear_state()

        # Clear DSPy's in-memory cache
        if hasattr(self.lm, "history"):
            self.lm.history = []

        # Clear DSPy's disk cache to force fresh LLM calls
        cache_dir = os.path.expanduser("~/.dspy_cache")
        if os.path.exists(cache_dir):
            with contextlib.suppress(Exception):
                shutil.rmtree(cache_dir)

    def chat(self, question: str) -> str:
        """Main entry point."""

        # 0. Pre-Classification (Main Agent Level)
        # Check if it's purely informational or needs search
        history_str = ""
        for turn in self.history[-3:]:
            history_str += f"User: {turn.get('question', '')}\n"
            history_str += f"Agent: {turn.get('answer', '')}\n"

        intent_pred = self.intent_classifier(query=question, history=history_str)
        # intents = intent_pred.intents # Unused for now in main agent
        detected_language = intent_pred.language or "pt"

        # 1. Fund Search (Agentic Step)
        # Pass the already computed intent to avoid double cost/latency
        # CRITICAL FIX: Pass the full conversation history context to the search tool!
        # The search tool needs to know about previous entities (like "GLP") referenced in history
        # to resolve follow-up queries like "fund with this name" correctly.

        # We construct a context-aware query if history exists
        # context_aware_query = question # Unused logic placeholder
        if self.history:
            # We don't change the question itself, but we ensure the search tool has access
            # to history via its own update_history method which we call at the end of chat().
            # However, for the CURRENT call, the search tool's state might be stale if we don't
            # explicitly pass history or if the tool relies on 'ask' parameter context.
            # In the current implementation of FundSearchTool.ask(), it doesn't take history as arg,
            # but relies on its internal state.
            pass

        search_output: SearchOutput = self.search_tool.ask(question, intent_prediction=intent_pred)

        # 2. Process Output
        cnpjs = search_output.cnpjs
        response_type = search_output.response_type

        fund_results = []

        # If we have CNPJs and it's a result-oriented response, fetch details
        if cnpjs and response_type in [
            "single_match",
            "list_results",
            "too_many_results",
            "disambiguation",
        ]:
            # Limit results based on confidence logic inferred from response_type/count
            # "if fund_search tool is very confident in 1/2/3 funds... show only these 2/3"
            # "if it has some good answers show 5"
            # "if generic... show 10"

            # Default behavior: show top 10 (user requested more visibility)
            limit = 10

            # If very few results (<4), show all of them (high confidence implicit in low count + match)
            if len(cnpjs) < 4:
                limit = len(cnpjs)
            # If explicitly ambiguous or "too many results" flag, maybe show more to help disambiguate?
            elif response_type == "too_many_results":
                limit = 10  # Show more to help user filter
            elif response_type == "disambiguation":
                limit = 5  # Show top 5 candidates for disambiguation

            # Fetch details for top N
            target_cnpjs = cnpjs[:limit]
            fund_results = self.details_tool(target_cnpjs)

        # 3. Generate Final Response
        answer = self._generate_response(
            question=question,
            results=fund_results,
            response_type=response_type,
            interpretation_note=search_output.interpretation_note,
            suggested_followup=search_output.suggested_followup,
            suggestions=search_output.suggestions,
            user_language="pt"
            if detected_language == "pt"
            else detected_language,  # Enforce PT if detected
        )

        # Save history
        self.history.append({"question": question, "answer": answer})

        # Update Search Tool's history for context awareness
        # IMPORTANT: This allows the next turn to know about entities found in this turn
        self.search_tool.update_history(question, answer)

        return answer

    def _generate_response(
        self,
        question: str,
        results: list,
        response_type: str,
        interpretation_note: str | None,
        suggested_followup: str | None,
        suggestions: list[str],
        user_language: str = "pt",
    ) -> str:
        response_pred = self.response_generator(
            query=question,
            results=results,
            response_type=response_type,
            user_language=user_language,
            interpretation_note=interpretation_note,
        )

        final_text = response_pred.answer

        # Append explicit follow-up suggestions if provided by Search Agent
        if suggested_followup:
            final_text += f"\n\n{suggested_followup}"

        if suggestions:
            final_text += "\nSuggestions:\n" + "\n".join([f"- {opt}" for opt in suggestions])

        return final_text
