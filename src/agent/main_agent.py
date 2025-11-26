import dspy

from src.agent.fund_details.tool import FundDetailsTool
from src.agent.fund_search.models.output import SearchOutput
from src.agent.fund_search.modules.intent import IntentClassifier
from src.agent.fund_search.orchestrator import FundSearchTool
from src.agent.response.generator import ResponseGenerator


class MainAgent:
    """
    Main Agent Orchestrator.
    Combines FundSearchTool (Discovery) and FundDetailsTool (Retrieval).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
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
        self.response_generator = ResponseGenerator()

        # Classifier for MainAgent to decide flow
        self.intent_classifier = IntentClassifier()

        # State
        self.history = []

    def get_history(self) -> list[dict[str, str]]:
        """Return conversation history."""
        return self.history

    def reset_history(self):
        """Reset conversation history."""
        self.history = []
        self.search_tool.clear_state()

    def chat(self, question: str) -> str:
        """Main entry point."""

        # 0. Pre-Classification (Main Agent Level)
        # Check if it's purely informational or needs search
        history_str = ""
        for turn in self.history[-3:]:
            history_str += f"User: {turn.get('question', '')}\n"
            history_str += f"Agent: {turn.get('answer', '')}\n"

        intent_pred = self.intent_classifier(query=question, history=history_str)
        intents = intent_pred.intents
        detected_language = intent_pred.language or "pt"

        # Handle Informational directly
        if "informational" in intents:
            answer = self._generate_response(
                question=question,
                results=[],
                response_type="informational",
                interpretation_note=intent_pred.interpretation_note,
                suggested_followup=None,
                suggestions=[],
                user_language=detected_language,
            )
            self.history.append({"question": question, "answer": answer})
            # Also update search tool history so it knows we chatted
            self.search_tool.update_history(question, answer)
            return answer

        # 1. Fund Search (Agentic Step)
        # Pass the already computed intent to avoid double cost/latency
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

            # Default behavior: show top 5
            limit = 5

            # If very few results (<4), show all of them (high confidence implicit in low count + match)
            if len(cnpjs) < 4:
                limit = len(cnpjs)
            # If explicitly ambiguous or "too many results" flag, maybe show more to help disambiguate?
            elif response_type == "too_many_results":
                limit = 5  # Keep it focused even if many
            elif response_type == "disambiguation":
                limit = 3  # Show top 3 candidates for disambiguation

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
            user_language=search_output.detected_language,
        )

        # Save history
        self.history.append({"question": question, "answer": answer})

        # Update Search Tool's history for context awareness
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
