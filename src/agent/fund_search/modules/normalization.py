import dspy

from src.agent.fund_search.utils.mappings import EntityMapper


class EntityNormalizationSignature(dspy.Signature):
    """
    Normalize a user-provided entity name to its canonical form.

    Used for PROVIDER normalization (fund managers, banks).

    The user may provide misspelled names, nicknames, or partial names.
    The goal is to output the standardized name used in financial databases.

    Examples:
    - "XP Investimentos" -> "XP"
    - "BTG Pactual Asset" -> "BTG PACTUAL"
    - "banco do brasil" -> "BANCO DO BRASIL"
    """

    query_text = dspy.InputField(desc="The raw text containing the entity name")
    entity_type = dspy.InputField(desc="Type of entity: 'PROVIDER' (bank/manager)")

    normalized_name = dspy.OutputField(desc="The canonical name or primary ticker.")
    entity_category = dspy.OutputField(
        desc="Category of the entity if known (e.g., EQUITY, FUND, DERIVATIVES, BANK, MANAGER).",
        format=str,
    )  # Using str to allow flexibility, but could be Literal
    confidence = dspy.OutputField(desc="Confidence score (0.0-1.0)")
    is_ambiguous = dspy.OutputField(desc="True if the input refers to multiple entities")


class EntityNormalizer(dspy.Module):
    """
    DSPy module for intelligent entity normalization.

    Normalizes PROVIDER entities (fund managers, banks)
    - Maps variations like "XP Investimentos", "XP Asset" -> "XP"
    - Uses deterministic mapping via EntityMapper for fast lookups
    - Falls back to LLM if no direct match found
    """

    def __init__(self):
        super().__init__()
        self.normalize_prog = dspy.ChainOfThought(EntityNormalizationSignature)

    def forward(self, query_text: str, entity_type: str = "PROVIDER"):
        """
        Normalize PROVIDER entity name to canonical form.

        Args:
            query_text: Raw entity name from user query
            entity_type: Must be "PROVIDER"

        Returns:
            dspy.Prediction with normalized_name, entity_category, confidence, is_ambiguous
        """
        # Check deterministic mappings (Fast Path)
        if entity_type == "PROVIDER":
            direct_match = EntityMapper.normalize_provider(query_text)
            if direct_match:
                return dspy.Prediction(
                    normalized_name=direct_match,
                    entity_category="PROVIDER",
                    confidence=1.0,
                    is_ambiguous=False,
                )

        # If no direct match, use LLM
        return self.normalize_prog(query_text=query_text, entity_type=entity_type)
