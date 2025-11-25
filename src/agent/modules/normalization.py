import dspy

from src.agent.utils.mappings import AssetMapper, EntityMapper


class EntityNormalizationSignature(dspy.Signature):
    """
    Normalize a user-provided entity name to its canonical form or ticker/key.

    The user may provide misspelled names, nicknames, or partial names.
    The goal is to output the standardized name used in financial databases.

    Examples:
    - "rede odr" -> "Rede D'Or" (or ticker RDOR3)
    - "magalu" -> "Magazine Luiza" (or ticker MGLU3)
    - "banco do brasil" -> "BB" (Provider Key) or "BBAS3" (Asset Ticker)
    - "petr4" -> "PETR4"
    """

    query_text = dspy.InputField(desc="The raw text containing the entity name")
    entity_type = dspy.InputField(
        desc="Type of entity: 'ASSET' (stock/bond/fund) or 'PROVIDER' (bank/manager)"
    )

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
    """

    def __init__(self):
        super().__init__()
        self.normalize_prog = dspy.ChainOfThought(EntityNormalizationSignature)

    def forward(self, query_text: str, entity_type: str = "ASSET"):
        # 1. First, check deterministic mappings (Fast Path)
        if entity_type == "PROVIDER":
            direct_match = EntityMapper.normalize_provider(query_text)
            if direct_match:
                return dspy.Prediction(
                    normalized_name=direct_match,
                    entity_category="PROVIDER",  # Generic category for providers
                    confidence=1.0,
                    is_ambiguous=False,
                )
        elif entity_type == "ASSET":
            # Check for direct ticker match or name match in our extract
            tickers = AssetMapper.get_tickers(query_text)
            if tickers:
                # Return the first ticker as normalized name
                # We don't easily know the category here without reverse lookup,
                # but we can assume it's valid.
                # Ideally AssetMapper.get_tickers could return category too, but let's keep it simple.
                return dspy.Prediction(
                    normalized_name=tickers[0],
                    entity_category="UNKNOWN",  # Or infer from ticker pattern?
                    confidence=1.0,
                    is_ambiguous=len(tickers) > 1,
                )

        # 2. If no direct match, use LLM
        return self.normalize_prog(query_text=query_text, entity_type=entity_type)
