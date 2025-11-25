import difflib
import os

import dspy

import mlflow
from src.agent.models.state import ConversationState
from src.agent.modules.extraction import SpecializedExtractor
from src.agent.modules.intent import IntentClassifier
from src.agent.modules.manager import ConversationManager
from src.agent.modules.response import ResponseGenerator
from src.agent.modules.search_manager import SearchManager
from src.agent.utils.tracing import TracingManager


class FundSearchOrchestrator:
    """
    Orchestrates the fund search agent pipeline using DSPy modules.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        enable_mlflow: bool = True,
        mlflow_tracking_uri: str | None = None,
        mlflow_experiment_name: str = "FundSearch-Agent",
    ):
        """Initialize the orchestrator and all sub-modules."""

        # 1. Setup DSPy / LLM
        self.lm = dspy.LM(model=f"openai/{model}", api_key=api_key)
        dspy.configure(lm=self.lm)

        # 2. Setup MLflow Tracing
        if enable_mlflow:
            tracking_uri = mlflow_tracking_uri or os.getenv(
                "MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"
            )
            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment(mlflow_experiment_name)
            mlflow.openai.autolog()

        # 3. Initialize Tracing Manager
        self.tracer = TracingManager(enabled=enable_mlflow)

        # 4. Initialize Pipeline Modules
        self.intent_classifier = IntentClassifier()
        self.extractor = SpecializedExtractor()
        self.search_manager = SearchManager(tracer=self.tracer)
        self.conversation_manager = ConversationManager()
        self.response_generator = ResponseGenerator()

        # 5. Initialize State
        self.state = ConversationState()

    def chat(self, question: str) -> str:
        """Chat wrapper that uses history."""
        return self.ask(question, use_history=True)

    def get_history(self) -> list[dict[str, str]]:
        """Return conversation history."""
        return self.state.history

    def ask(self, question: str, use_history: bool = True) -> str:
        """Main entry point for processing a user query."""
        with self.tracer.chain(
            "FundSearchOrchestrator",
            inputs={"question": question, "use_history": use_history},
        ) as root_span:
            root_span.set_attribute("turn", self.state.turn + 1)
            answer = self._process_query(question, use_history)
            root_span.set_outputs({"answer": answer})
            return answer

    def _process_query(self, question: str, use_history: bool) -> str:
        """Internal implementation of query processing."""
        if not use_history:
            self.state.clear()

        self.state.last_query = question
        self.state.turn += 1

        # --- PHASE 1: INTENT CLASSIFICATION ---
        with self.tracer.llm_call("IntentClassification", {"query": question}) as span:
            intent_pred = self.intent_classifier(query=question)
            intents = intent_pred.intents
            detected_language = intent_pred.language or "pt"
            search_query = intent_pred.search_query  # Optimized query for semantic search
            required_name_terms = intent_pred.required_name_terms
            is_potentially_ambiguous = intent_pred.is_potentially_ambiguous
            interpretation_note = intent_pred.interpretation_note
            span.set_outputs(
                {
                    "intents": intents,
                    "language": detected_language,
                    "search_query": search_query,
                    "required_name_terms": required_name_terms,
                    "is_potentially_ambiguous": is_potentially_ambiguous,
                    "interpretation_note": interpretation_note,
                }
            )

        # --- PHASE 2: EXTRACTION ---
        with self.tracer.llm_call(
            "CriteriaExtraction",
            {"query": question, "intents": intents, "search_query": search_query},
        ) as span:
            extractor_pred = self.extractor(
                query=question,
                intents=intents,
                language=detected_language,
                search_query=search_query,  # Pass optimized query for semantic search
                required_name_terms=required_name_terms,
            )
            parsed_query = extractor_pred.parsed_query
            span.set_outputs({"parsed_query": parsed_query.to_dict()})

        # Merge with historical criteria (context retention)
        self.state.merge_criteria(parsed_query.to_dict())

        # --- APPLY HISTORICAL CRITERIA ---
        for key, value in self.state.accumulated_criteria.items():
            if hasattr(parsed_query, key) and getattr(parsed_query, key) is None:
                # Special handling for Pydantic models stored as dicts in state
                if key == "numeric_filter" and isinstance(value, dict):
                    from src.agent.models.query import NumericFilter

                    value = NumericFilter(**value)

                setattr(parsed_query, key, value)

        # --- PHASE 2b: CONTEXT RESOLUTION ---
        # If the user is asking about a fund by name that exists in previous results,
        # resolve it to a specific fund ID to ensure exact retrieval.
        if self.state.last_results and parsed_query.semantic_query:
            # Create map of name -> fund_id from last results
            name_map = {r.legal_name: r.fund_id for r in self.state.last_results if r.legal_name}
            candidate_names = list(name_map.keys())

            # Find closest match
            matches = difflib.get_close_matches(
                parsed_query.semantic_query, candidate_names, n=1, cutoff=0.85
            )

            if matches:
                matched_name = matches[0]
                matched_id = name_map[matched_name]
                parsed_query.targeted_fund_ids = [matched_id]

        # --- GET CONTEXT FUND IDs ---
        context_fund_ids = (
            [r.fund_id for r in self.state.last_results] if self.state.last_results else None
        )

        # --- PHASE 3: CONVERSATION CHECK (Pre-Search) ---
        should_ask, question_text, options = self.conversation_manager.should_ask_followup(
            parsed_query, [], self.state, search_performed=False
        )

        if should_ask:
            self.state.awaiting_clarification = True
            return self._format_followup(question_text, options)

        # --- Special Path: Informational Intent ---
        if "informational" in intents:
            return self._generate_response(question, [], "informational", detected_language)

        # --- PHASE 4: SEARCH EXECUTION ---
        with self.tracer.chain("SearchExecution", {"parsed_query": parsed_query.to_dict()}) as span:
            search_pred = self.search_manager(parsed_query, context_fund_ids=context_fund_ids)
            merged_results = search_pred.merged_results
            results = merged_results.items
            span.set_outputs(
                {
                    "result_count": len(results),
                    "has_ambiguity": merged_results.has_ambiguity,
                    "semantic_count": merged_results.semantic_count,
                    "structured_count": merged_results.structured_count,
                }
            )

        self.state.last_results = results

        # --- PHASE 5: CONVERSATION CHECK (Post-Search) ---
        if merged_results.has_ambiguity:
            self.state.awaiting_selection = True
            return self._generate_response(
                question,
                merged_results.disambiguation_candidates,
                "disambiguation",
                detected_language,
                interpretation_note,
            )

        should_ask, question_text, options = self.conversation_manager.should_ask_followup(
            parsed_query,
            [r.model_dump() for r in results],
            self.state,
            search_performed=True,
        )

        if should_ask:
            # If no results found, skip "No results" generation and just ask follow-up
            # This avoids "I wasn't able to find..." when the query was just vague
            if not results:
                return self._format_followup(question_text, options)

            response_type = "too_many_results"
            answer = self._generate_response(
                question, results[:5], response_type, detected_language, interpretation_note
            )
            answer += f"\n\n{question_text}"
            if options:
                answer += "\nSuggestions:\n" + "\n".join([f"- {opt}" for opt in options])
            return answer

        # --- PHASE 6: FINAL RESPONSE ---
        response_type = "single_match" if len(results) == 1 else "list_results"
        if not results:
            response_type = "no_results"

        answer = self._generate_response(
            question, results[:20], response_type, detected_language, interpretation_note
        )

        if use_history:
            self.state.history.append({"question": question, "answer": answer})

        return answer

    def _generate_response(
        self,
        question: str,
        results: list,
        response_type: str,
        language: str,
        interpretation_note: str | None = None,
    ) -> str:
        """Generate response with tracing."""
        with self.tracer.llm_call(
            "ResponseGeneration",
            {
                "response_type": response_type,
                "result_count": len(results),
                "interpretation_note": interpretation_note,
            },
        ) as span:
            response_pred = self.response_generator(
                query=question,
                results=results,
                response_type=response_type,
                user_language=language,
                interpretation_note=interpretation_note,
            )
            span.set_outputs({"answer": response_pred.answer})
            return response_pred.answer

    def _format_followup(self, question: str, options: list[str]) -> str:
        """Helper to format follow-up questions."""
        response = f"{question}\n"
        if options:
            response += "\nSuggestions:\n" + "\n".join([f"- {opt}" for opt in options])
        return response

    def reset_history(self):
        self.state.clear()
