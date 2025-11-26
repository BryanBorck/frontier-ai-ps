import json

import dspy

from src.agent.fund_search.models.query import ParsedQuery
from src.agent.fund_search.models.state import ConversationState
from src.agent.fund_search.signatures.followup import FollowUpSignature


class ConversationManager(dspy.Module):
    """
    Manages the conversation flow, deciding when to ask follow-up questions.
    Uses a hybrid approach: deterministic rules for speed + LLM for natural phrasing.
    """

    def __init__(self):
        super().__init__()
        self.generate_followup = dspy.ChainOfThought(FollowUpSignature)

    def should_ask_followup(
        self,
        parsed: ParsedQuery,
        results: list[dict],
        state: ConversationState,
        search_performed: bool = False,
    ) -> tuple[bool, str, list[str]]:
        """
        Decide if we should ask a follow-up, and generate it if so.
        Returns: (should_ask, question_text, suggested_options)
        """

        # RULE 0: Informational/Explain Intent -> NEVER ask follow-up, just answer
        if "informational" in parsed.intents:
            return (False, "", [])

        # RULE 1: Empty Query -> Always ask
        # Only if it's not a semantic query or informational
        if parsed.is_empty() and state.turn == 0 and not parsed.semantic_query:
            return self._generate_initial_followup(parsed)

        # RULE 1.5: Vague Query Pre-Search -> Ask for refinement
        # If user only specifies a provider or type without details, ask before searching
        if not search_performed and self._is_vague_query(parsed):
            return self._generate_refinement_followup(parsed)

        # RULE 2: Too many results (>30) -> Suggest narrowing
        # Only applies if we actually searched
        if search_performed and len(results) > 30:
            return self._generate_narrowing_followup(parsed, results)

        # RULE 3: No results -> Suggest alternatives
        # Only applies if we actually searched and found nothing
        if search_performed and len(results) == 0:
            return self._generate_no_results_followup(parsed)

        return (False, "", [])

    def _generate_initial_followup(self, parsed: ParsedQuery) -> tuple[bool, str, list[str]]:
        """Generate open-ended starting question."""
        result = self.generate_followup(
            query=parsed.query,
            parsed_so_far="{}",
            result_count=0,
            user_language=parsed.detected_language,
        )
        return True, result.follow_up_question, result.suggested_options

    def _generate_narrowing_followup(
        self, parsed: ParsedQuery, results: list[dict]
    ) -> tuple[bool, str, list[str]]:
        """Generate question to filter down results."""
        # Simple distribution stats to help LLM
        context = {
            "already_specified": parsed.to_dict(),
            "count": len(results),
            "note": "Too many results, need to filter by class, type, or audience",
        }

        result = self.generate_followup(
            query=parsed.query,
            parsed_so_far=json.dumps(context),
            result_count=len(results),
            user_language=parsed.detected_language,
        )
        return True, result.follow_up_question, result.suggested_options

    def _generate_no_results_followup(self, parsed: ParsedQuery) -> tuple[bool, str, list[str]]:
        """Generate help for zero results."""
        result = self.generate_followup(
            query=parsed.query,
            parsed_so_far=json.dumps(parsed.to_dict()),
            result_count=0,
            user_language=parsed.detected_language,
        )
        return True, result.follow_up_question, result.suggested_options

    def _is_vague_query(self, parsed: ParsedQuery) -> bool:
        """Check if query is too broad to search immediately."""
        # If specific numeric filter (AUM, return), it's specific
        if parsed.numeric_filter:
            return False

        # If semantic query has enough context (e.g. "bradesco gold"), specific
        # Simple heuristic: if intent generated a descriptive query > 1 word (excl provider)
        # But "bradesco" is 1 word. "bradesco funds" -> "bradesco".
        # "bradesco gold" -> "fundo bradesco investimento em ouro".
        if parsed.semantic_query and len(parsed.semantic_query.split()) > 2:
            return False

        # If exact match, specific
        if parsed.is_exact_match:
            return False

        # Check structured criteria
        criteria = parsed.to_dict()
        keys_to_ignore = [
            "query",
            "intents",
            "detected_language",
            "semantic_query",
            "needs_followup",
            "required_name_terms",
        ]
        active_filters = [k for k in criteria if k not in keys_to_ignore]

        # Relaxed Vague Check:
        # Allow single-filter searches (e.g. "Itau funds", "Multimercado") to proceed to search.
        # Post-search logic (Rule 2) will handle "Too many results" if needed.
        # This prevents the "Are you sure?" loop when user says "all".
        return len(active_filters) == 0

    def _generate_refinement_followup(self, parsed: ParsedQuery) -> tuple[bool, str, list[str]]:
        """Generate question to refine a vague query."""
        # We simulate a high result count to prompt the LLM to ask for narrowing
        result = self.generate_followup(
            query=parsed.query,
            parsed_so_far=json.dumps(parsed.to_dict()),
            result_count=1000,
            user_language=parsed.detected_language,
        )
        return True, result.follow_up_question, result.suggested_options
