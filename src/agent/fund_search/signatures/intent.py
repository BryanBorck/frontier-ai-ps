from typing import Literal

import dspy


class IntentClassificationSignature(dspy.Signature):
    """
    Classify the given query to determine which search tools to use for retrieving fund information. The task involves discerning user intent accurately using domain-specific knowledge about financial funds and search tools. Below are the detailed instructions and mappings for this task, ensuring that user queries are interpreted precisely to direct the query to the appropriate search tool.

    ### TOOL MAPPING:
    - **find_by_name** → Use SemanticSearchTool for queries that explicitly reference a specific fund name. This requires identifying genuinely existing fund names.
    - **find_by_strategy** → Use SemanticSearchTool to interpret queries that imply a particular theme, sector, or investment concept, even if not explicitly stated.
    - **find_by_criteria** → Use FundSearchTool for queries that explicitly mention structured database filters or fund types.
    - **find_by_exposure** → Use PositionSearchTool to find funds based on their asset holdings exposure.
    - **has_numeric_filter** → Use SnapshotSearchTool or PerformanceSearchTool if the query involves numeric filters.

    ### INTERPRET USER INTENT:
    - Analyze the query to deduce the actual information the user is seeking.
    - Use domain-specific knowledge about funds and investment sectors; if a fund name doesn't appear to exist, consider the investment theme instead.

    #### EXAMPLES:
    - "bradesco gold fund" implies the user wants a Bradesco fund tracking gold prices, not a non-existent fund named "Bradesco Gold".
    - "itau tech fund" implies interest in an Itau fund focused on the tech sector, even if "Itau Tech" is not a literal fund name.
    - "multimarket low risk" implies the user is interested in a multimarket fund assessed qualitatively as low risk.

    #### IDENTIFIER FOR FIND_BY_NAME:
    - Use when queries have specific existing fund names such as "Verde Scena", "Alaska Black", etc.

    ### EXPLICIT FILTERS (find_by_criteria):
    - "FIP funds", "funds for qualified investors", "multimercado funds" indicate using **find_by_criteria**.
    - Standard Asset Classes: "Fixed Income" (Renda Fixa), "Equities" (Ações), "Multimarket" (Multimercado) are **find_by_criteria** (they are strict filters).
    - Managers: "Bradesco funds", "Now Itau", "E da Bradesco?" are **find_by_criteria** (Manager filter).
    - Audiences: "For retail", "Qualified investors", "Professional" are **find_by_criteria**.
    - Tax/Benefits: "Long term tax", "Tax free" are **find_by_criteria**.
    - **HARD RULE**: If it's a standard category (Class, Type, Manager, Audience), use **find_by_criteria**, NOT strategy.

    ### COMPARATIVE & NUMERIC (has_numeric_filter):
    - specific numbers: "Top 5", "AUM > 1B".
    - comparative adjectives: "Cheaper" (min fee), "Better performing" (max return), "Larger" (max AUM), "Most popular" (max investors), "Os menores" (min size).
    - These imply sorting/filtering by a metric → **has_numeric_filter**.

    ### EXPOSURE (find_by_exposure):
    - Tickers: "PETR4", "VALE3", "AAPL34".
    - "Exposure to X", "holding Y".

    ### PAGINATION / CONTINUATION (general_browse):
    - "do you have more?" implies **general_browse**.
    - "show me 10 more" suggests combining **general_browse** with **has_numeric_filter**.
    - "What do you recommend?", "Details please", "What else?" -> **general_browse** (Request for results/action).
    - Conversational queries ("Hi", "Hello") should be mapped to **general_browse** or ignored, but NOT informational.

    ### CLARIFICATION:
    - Only seek clarification when the query is genuinely ambiguous with multiple equally valid interpretations. This is typically not required for straightforward "manager + theme" queries.

    Use your expertise to interpret the user's intent beyond literal keyword matching and ensure the query maps to the most appropriate tool to retrieve relevant fund information.
    """

    query: str = dspy.InputField(desc="User's natural language query about funds")
    history: str = dspy.InputField(desc="Conversation history (previous questions and answers)")

    intents: list[
        Literal[
            "find_by_name",  # Specific fund names: "Verde Scena", "Alaska Black"
            "find_by_strategy",  # Theme/sector + optional manager: "bradesco gold", "tech funds", "ESG"
            "find_by_criteria",  # Structured filters: fund_type, investment_class, audience
            "find_by_exposure",  # Asset holdings: "holding Petrobras", "invested in VALE3"
            "has_numeric_filter",  # Numbers/Sorting: "AUM > 200M", "top 10", "cheapest", "best performing"
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
