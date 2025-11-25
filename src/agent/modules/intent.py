import dspy

from src.agent.signatures.intent import IntentClassificationSignature


class IntentClassifier(dspy.Module):
    """
    Module for classifying user queries into intents.
    Uses LLM knowledge to interpret user intent and optimize search queries.
    """

    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(IntentClassificationSignature)

    def forward(self, query: str) -> dspy.Prediction:
        """
        Classify the query and return intents, optimized search query, and clarification info.
        """
        result = self.classify(query=query)

        # Ensure intents is a list
        intents = result.intents
        if isinstance(intents, str):
            intents = [intents]

        return dspy.Prediction(
            intents=intents,
            language=result.language,
            search_query=result.search_query,  # Optimized query for semantic search
            required_name_terms=result.required_name_terms,
            is_potentially_ambiguous=result.is_potentially_ambiguous,
            interpretation_note=result.interpretation_note,
        )
