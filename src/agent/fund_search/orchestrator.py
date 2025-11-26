import dspy

from src.agent.fund_search.models.output import SearchOutput
from src.agent.fund_search.models.state import ConversationState
from src.agent.fund_search.modules.extraction import SpecializedExtractor
from src.agent.fund_search.modules.intent import IntentClassifier
from src.agent.fund_search.modules.manager import ConversationManager
from src.agent.fund_search.modules.search_manager.manager import SearchManager
from src.agent.fund_search.utils.tracing import TracingManager
from src.infrastructure.logging.config import setup_mlflow


class FundSearchTool:
    """
    Tool for searching funds and returning CNPJs.
    Wraps the agentic workflow for fund discovery.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        enable_mlflow: bool = True,
        mlflow_tracking_uri: str | None = None,
        mlflow_experiment_name: str = "FundSearch-Agent",
    ):
        """Initialize the agent and all sub-modules."""

        # 1. Setup DSPy / LLM
        self.lm = dspy.LM(model=f"openai/{model}", api_key=api_key)
        dspy.configure(lm=self.lm)

        # 2. Setup MLflow Tracing
        if enable_mlflow:
            setup_mlflow(experiment_name=mlflow_experiment_name, tracking_uri=mlflow_tracking_uri)

        # 3. Initialize Tracing Manager
        self.tracer = TracingManager(enabled=enable_mlflow)

        # 4. Initialize Pipeline Modules
        self.intent_classifier = IntentClassifier()
        self.extractor = SpecializedExtractor()
        self.search_manager = SearchManager(tracer=self.tracer)
        self.conversation_manager = ConversationManager()

        # 5. Initialize State
        self.state = ConversationState()

    def ask(
        self,
        question: str,
        context_cnpjs: list[str] | None = None,
        use_history: bool = True,
        intent_prediction: dspy.Prediction | None = None,
    ) -> SearchOutput:
        """Main entry point for processing a user query."""
        with self.tracer.chain(
            "FundSearchTool",
            inputs={
                "question": question,
                "context_cnpjs_count": len(context_cnpjs) if context_cnpjs else 0,
            },
        ) as root_span:
            root_span.set_attribute("turn", self.state.turn + 1)
            output = self._process_query(question, context_cnpjs, use_history, intent_prediction)
            root_span.set_outputs(
                {
                    "cnpjs_count": len(output.cnpjs),
                    "response_type": output.response_type,
                }
            )
            return output

    def _process_query(
        self,
        question: str,
        context_cnpjs: list[str] | None,
        use_history: bool,
        intent_prediction: dspy.Prediction | None = None,
    ) -> SearchOutput:
        """Internal implementation of query processing."""
        if not use_history:
            self.state.clear()

        # Pass a simplified history string to the classifier
        # Format: "User: ... \n Agent: ..."
        history_str = ""
        for turn in self.state.history[-3:]:  # Last 3 turns context
            history_str += f"User: {turn.get('question', '')}\n"
            history_str += f"Agent: {turn.get('answer', '')}\n"

        self.state.last_query = question
        self.state.turn += 1

        # --- PHASE 1: INTENT CLASSIFICATION ---
        if intent_prediction:
            intent_pred = intent_prediction
            # Extract fields (assuming structure matches)
            intents = intent_pred.intents
            detected_language = intent_pred.language or "pt"
            search_query = intent_pred.search_query
            required_name_terms = intent_pred.required_name_terms
            is_ambiguous = intent_pred.is_potentially_ambiguous
            interpretation_note = intent_pred.interpretation_note
            context_status = getattr(intent_pred, "context_status", "keep")
        else:
            with self.tracer.llm_call("IntentClassification", {"query": question}) as span:
                # Pass history to classifier
                intent_pred = self.intent_classifier(query=question, history=history_str)
                intents = intent_pred.intents
                detected_language = intent_pred.language or "pt"
                search_query = intent_pred.search_query
                required_name_terms = intent_pred.required_name_terms
                is_ambiguous = intent_pred.is_potentially_ambiguous
                interpretation_note = intent_pred.interpretation_note
                context_status = getattr(
                    intent_pred, "context_status", "keep"
                )  # Default to keep if not present

                span.set_outputs(
                    {
                        "intents": intents,
                        "language": detected_language,
                        "search_query": search_query,
                        "is_ambiguous": is_ambiguous,
                        "context_status": context_status,
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
                search_query=search_query,
                required_name_terms=required_name_terms,
            )
            parsed_query = extractor_pred.parsed_query
            span.set_outputs({"parsed_query": parsed_query.to_dict()})

        # --- CONTEXT MANAGEMENT ---
        # Handle context status from classifier
        active_context = None

        if context_status == "reset":
            # Clear accumulated criteria and ignore previous CNPJs
            self.state.accumulated_criteria = {}
            active_context = None
        elif context_status == "refine_result_set":
            # Use previous CNPJs to filter
            active_context = context_cnpjs if context_cnpjs is not None else self.state.last_cnpjs
        else:  # "keep" / refinement
            # Don't use context_cnpjs (to avoid truncation), just rely on accumulated criteria
            # UNLESS we don't have new criteria but just a numeric filter?
            # Generally, if we are refining criteria, we want a fresh search with merged criteria.
            active_context = None

        # Merge with historical criteria (context retention)
        # If we reset, accumulated_criteria is empty, so we just set new ones.
        self.state.merge_criteria(parsed_query.to_dict())

        # --- APPLY HISTORICAL CRITERIA ---
        for key, value in self.state.accumulated_criteria.items():
            if hasattr(parsed_query, key) and getattr(parsed_query, key) is None:
                if key == "numeric_filter" and isinstance(value, dict):
                    from src.agent.fund_search.models.query import NumericFilter

                    value = NumericFilter(**value)
                setattr(parsed_query, key, value)

        # --- PHASE 3: CONVERSATION CHECK (Pre-Search) ---
        # We pass empty results list because we haven't searched yet
        should_ask, question_text, options = self.conversation_manager.should_ask_followup(
            parsed_query, [], self.state, search_performed=False
        )

        if should_ask:
            self.state.awaiting_clarification = True
            return SearchOutput(
                cnpjs=[],
                response_type="followup",
                suggested_followup=question_text,
                suggestions=options,
                interpretation_note=interpretation_note,
                detected_language=detected_language,
                is_ambiguous=is_ambiguous,
            )

        # --- PHASE 4: SEARCH EXECUTION ---
        with self.tracer.chain("SearchExecution", {"parsed_query": parsed_query.to_dict()}) as span:
            search_pred = self.search_manager(parsed_query, context_cnpjs=active_context)
            results = search_pred.cnpjs
            span.set_outputs({"result_count": len(results)})

        self.state.last_cnpjs = results

        # --- PHASE 5: CONVERSATION CHECK (Post-Search) ---
        should_ask, question_text, options = self.conversation_manager.should_ask_followup(
            parsed_query,
            [{"cnpj": c} for c in results],  # Hack to satisfy length check in manager
            self.state,
            search_performed=True,
        )

        if should_ask:
            # If no results found
            if not results:
                return SearchOutput(
                    cnpjs=[],
                    response_type="no_results_followup",
                    suggested_followup=question_text,
                    suggestions=options,
                    interpretation_note=interpretation_note,
                    detected_language=detected_language,
                    is_ambiguous=is_ambiguous,
                )

            return SearchOutput(
                cnpjs=results,
                response_type="too_many_results",
                suggested_followup=question_text,
                suggestions=options,
                interpretation_note=interpretation_note,
                detected_language=detected_language,
                is_ambiguous=is_ambiguous,
            )

        # --- PHASE 6: FINAL RESPONSE ---
        response_type = "single_match" if len(results) == 1 else "list_results"
        if not results:
            response_type = "no_results"

        # Note: History update is handled by MainAgent, but we keep internal tracking if needed for future logic.
        # The current state.history is populated by MainAgent calling back? No, MainAgent manages its own history.
        # FundSearchAgent receives history implicitly via 'use_history' flag but doesn't receive the actual text unless passed.
        # Wait, FundSearchAgent.state has a history field.
        # We need to populate it for the classifier to work in the NEXT turn!

        # MainAgent adds to its own history.
        # FundSearchAgent needs to know about the answer it generated?
        # Actually, MainAgent generates the answer.
        # So FundSearchAgent doesn't know the final text.
        # We should pass the *previous* history into ask(), or rely on MainAgent to maintain state?
        # Currently MainAgent instantiates FundSearchAgent once.
        # We need a way to push the previous turn's QA into FundSearchAgent's state.

        # For now, we just pass the last 3 items from self.state.history.
        # But self.state.history is never updated with the ANSWER because the answer is generated outside!
        # We need to fix this.

        # Let's add a method `update_history(question, answer)` to FundSearchAgent.

        return SearchOutput(
            cnpjs=results,
            response_type=response_type,
            interpretation_note=interpretation_note,
            detected_language=detected_language,
            is_ambiguous=is_ambiguous,
        )

    def clear_state(self):
        self.state.clear()

    def update_history(self, question: str, answer: str):
        """Update internal history with the final Q&A pair."""
        self.state.history.append({"question": question, "answer": answer})
