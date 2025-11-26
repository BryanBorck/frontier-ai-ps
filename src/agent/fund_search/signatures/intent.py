from typing import Literal

import dspy


class IntentClassificationSignature(dspy.Signature):
    """
    Classify the query to determine WHICH SEARCH TOOLS to use.
    Use your knowledge to interpret what the user ACTUALLY means.

    TOOL MAPPING:
    - find_by_name → SemanticSearchTool (fuzzy name matching)
    - find_by_strategy → SemanticSearchTool (theme/sector/concept)
    - find_by_criteria → FundSearchTool (structured DB filters ONLY)
    - find_by_exposure → PositionSearchTool (asset holdings)
    - has_numeric_filter → SnapshotSearchTool/PerformanceSearchTool

    USE YOUR KNOWLEDGE TO INTERPRET USER INTENT:

    "bradesco gold fund" → [find_by_strategy]
      - User wants a Bradesco fund that tracks GOLD prices (like "Bradesco Ouro FIF")
      - NOT a fund literally named "Bradesco Gold" (that doesn't exist)
      - Search query: "fundo bradesco investimento em ouro"

    "itau tech fund" → [find_by_strategy]
      - User wants an Itau fund focused on TECHNOLOGY sector
      - NOT a fund literally named "Itau Tech"
      - Search query: "fundo itau setor de tecnologia"

    "verde crypto fund" → [find_by_strategy]
      - User wants a Verde Asset fund with crypto/blockchain exposure
      - Search query: "fundo verde cripto criptomoedas blockchain"

    "multimarket low risk" → [find_by_strategy]
      - "low risk" implies qualitative assessment (semantic).
      - Search query: "fundos multimercado baixo risco conservador"

    WHEN TO USE find_by_name (specific fund names):
    - "Verde Scena" → [find_by_name] (actual fund name)
    - "Alaska Black" → [find_by_name] (actual fund name)
    - "SPX Nimitz" → [find_by_name] (actual fund name)
    - "Dynamo Cougar" → [find_by_name] (actual fund name)

    WHEN TO USE find_by_criteria (explicit filters):
    - "FIP funds" → [find_by_criteria] (fund_type filter)
    - "funds for qualified investors" → [find_by_criteria] (audience filter)
    - "multimercado funds" → [find_by_criteria] (investment_class filter)

    PAGINATION / CONTINUATION:
    - "do you have more?" → [general_browse] (User wants more results from previous context)
    - "show me 10 more" → [general_browse, has_numeric_filter]

    CLARIFICATION - Only ask when TRULY ambiguous:
    - Query is too vague to determine intent
    - Multiple equally valid interpretations exist
    - NOT needed for "manager + theme" queries (use your knowledge!)
    """

    query: str = dspy.InputField(desc="User's natural language query about funds")
    history: str = dspy.InputField(desc="Conversation history (previous questions and answers)")

    intents: list[
        Literal[
            "find_by_name",  # Specific fund names: "Verde Scena", "Alaska Black"
            "find_by_strategy",  # Theme/sector + optional manager: "bradesco gold", "tech funds", "ESG"
            "find_by_criteria",  # Structured filters: fund_type, investment_class, audience
            "find_by_exposure",  # Asset holdings: "holding Petrobras", "invested in VALE3"
            "has_numeric_filter",  # Numbers: "AUM > 200M", "top 10"
            "informational",  # PURELY educational definitions: "What is FIDC?". NOT for "Show me more".
            "general_browse",  # Vague or PAGINATION request: "more results", "what else?", "browse funds"
        ]
    ] = dspy.OutputField(
        desc="List of intents. Use your knowledge to pick the RIGHT one, don't be overly cautious."
    )

    search_query: str = dspy.OutputField(
        desc="""Optimized Portuguese search query for semantic matching.
        - Translate English terms to Portuguese contextually.
        - Create a descriptive phrase that captures the fund's strategy, objective, or name.
        - Use natural language phrases to improve semantic matching.
        - NO QUOTES.
        Examples:
        - "bradesco gold fund" → fundo bradesco investimento em ouro
        - "itau tech fund" → fundo itau setor de tecnologia
        - "conservative funds" → fundos perfil conservador renda fixa
        - "verde scena" → verde scena
        """
    )

    required_name_terms: list[str] | None = dspy.OutputField(
        desc="""List of terms that MUST appear in the fund's name/description.
        USE SPARINGLY! Only for proper nouns, specific brands, or tickers.
        - "bradesco gold" → ["bradesco"] (Ouro is a strategy, let semantic handle it)
        - "petrobras funds" → ["petrobras"]
        - "tech funds" → None (leave 'tech' for semantic search)
        - "small caps" → None
        """
    )

    is_potentially_ambiguous: bool = dspy.OutputField(
        desc="""True if query COULD have multiple interpretations, even if we're confident.
        Examples of ambiguous queries:
        - "bradesco gold" → Could be fund NAME or fund STRATEGY (tracking gold)
        - "itau tech" → Could be fund NAME or fund STRATEGY (tech sector)
        Use this to offer follow-up clarification AFTER showing results."""
    )

    interpretation_note: str | None = dspy.OutputField(
        desc="""Brief note explaining your interpretation when is_potentially_ambiguous=True.
        Example: "I interpreted this as a Bradesco fund tracking gold prices (Bradesco Ouro)"
        None if query is not ambiguous."""
    )

    context_status: Literal["reset", "keep", "refine_result_set"] = dspy.OutputField(
        desc="""How to handle the previous conversation context (filters/results).
        - 'reset': Topic changed significantly (e.g. from 'Itau' to 'Bradesco', or 'Gold' to 'LatAm'). Discard old filters.
        - 'keep': Refining current topic (e.g. 'Itau funds' -> 'and only FIF'). Keep old filters and add new ones.
        - 'refine_result_set': Filtering specifically from the PREVIOUS LIST of results (e.g. 'which of these has highest fee?', 'show me the first one').
        """
    )

    language: Literal["pt", "en"] = dspy.OutputField(
        desc="""Detected language of the query text itself.
        - 'en' if the user is speaking English (e.g., "give me funds", "show me gold funds").
        - 'pt' if the user is speaking Portuguese (e.g., "me mostre fundos", "fundos de ouro").
        """
    )
