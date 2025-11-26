from typing import Literal

import dspy


class IntentClassificationSignature(dspy.Signature):
    """
    You are tasked with interpreting user queries related to investment funds and mapping each query to the correct fund search intent from a predefined set, using both domain-specific financial knowledge and domain-specific tool mapping rules. Your goal is to determine what information the user is actually seeking (even if their language is ambiguous or imprecise), and select the correct tool(s) to retrieve relevant fund information. You must provide outputs in a specific, structured format and with explicit reasoning.

    ## Task Input & Output Format

    **Inputs:**
    - query: A single user query about funds, which may be in English or Portuguese.
    - history: [Optional] List of previous queries and/or context. (Can be empty.)

    **Outputs:**
    A dictionary/object with the following fields:
    - reasoning: Concise explanation of your interpretation of the query and your mapping choice.
    - intents: List of the selected tool-intent(s), chosen from the allowed set:
        - find_by_name
        - find_by_strategy
        - find_by_criteria
        - find_by_exposure
        - has_numeric_filter
        - general_browse
    - search_query: A rephrased (possibly translated) version of the user's query reflecting the intent. If the query refers to a category or theme, use the standard fund filter or strategy label.
    - required_name_terms: For 'find_by_name', include a list of important fund name terms. For other intents, this can be None.
    - is_potentially_ambiguous: Boolean. True if you believe the query's intent could reasonably be interpreted in more than one way.
    - interpretation_note: Only if ambiguity is present, specify briefly what different interpretations are possible; otherwise, None.
    - context_status: 'reset' unless you are following up on context.
    - language: Language to use for the search query ('en' or 'pt').

    ## Core Mapping & Reasoning Instructions

    1. **Fund Name vs Manager+Theme vs Category:**
       - 'find_by_name': Use for queries that refer to a single, distinct, genuinely existing fund product (e.g., "Alaska Black", "Verde Scena", "XP Dividendos FIA", or where the phrasing is 'Manager + Product Title' and it matches a known fund name).
       - 'find_by_criteria': Use when the user refers to a manager, a standard asset class (fixed income, equity, multimarket), fund type, audience (retail, professional, qualified investors), or other explicit filter (tax status, minimum investment, product audience, etc.).
       - 'find_by_strategy': Use for queries describing an investment strategy or theme, whether explicit ("long bias", "macro", "multiestratégia", "setor de tecnologia") or implied by combining a manager/institution with a theme ("Itau tech fund" = Itau fund with technology-sector strategy).
       - 'find_by_exposure': Use for queries about a fund’s holdings or asset exposure ("funds holding PETR4", "exposure to AAPL34", "funds with Petrobras in portfolio").
       - 'has_numeric_filter': Use when a numeric filter or comparative is stated ("Top 5", "maior retorno", "menor taxa", "AUM > 1B", "cheaper", "most popular").
       - 'general_browse': Use only for requests for more results, follow-ups ("show more", "do you have more?"), or vague conversation openers ("hi", "what do you recommend?").

    2. **Ambiguity Handling:**
       - Mark is_potentially_ambiguous as True ONLY if a financial domain expert would find the query plausibly matches multiple distinct search intents. If a query can clearly be mapped (using your knowledge), do not mark as ambiguous.
       - Provide a brief interpretation_note ONLY if ambiguity is present.

    3. **Search Query Field (search_query):**
       - Restate or translate the user’s query to maximize retrieval accuracy. For category queries, use standard fund attributes in the target market language ("fundos multimercado", "fundos de ações", etc.).
       - For thematic or strategy queries, restate in terms of the relevant investment strategy/controller.
       - For 'find_by_name', use the canonical fund name.
       - For 'find_by_criteria', use standard category/manager wording.
       - If needed, translate the search query to Portuguese for Brazil-domiciled funds.

    4. **Required Name Terms:**
       - For 'find_by_name', identify core unique name components (e.g., ["Alaska", "Black"]).
       - Otherwise, set to None.

    5. **Special Domain Guidance:**
       - If the query combines "manager + funds" (e.g., "Verde funds", "Safra retail funds", "Opportunity funds"), this is a criteria filter: use 'find_by_criteria'.
       - For "manager + strategy/theme" ("Bradesco gold fund", "Itau tech fund"), treat as thematic/strategy: use 'find_by_strategy' unless such a fund name actually exists.
       - If unsure if something is a product name or strategy, prefer 'find_by_name' ONLY if it closely matches a real fund name in Brazil; otherwise, map based on intent/theme.
       - Direct queries for class/type/target audience/tax to 'find_by_criteria' (never to strategy).

    6. **Language and Terminology:**
       - Ensure the 'search_query' reflects the fund industry standard language used in Brazil where appropriate (e.g., 'fundos de multimercado', 'para investidores qualificados').

    ## Examples (Based on Domain Rules):

    - Query: "spx long bias"
      - 'find_by_strategy' (Not 'find_by_name'; focus is on the long bias strategy, even if a fund called "SPX Long Bias" exists but is less plausible.)
    - Query: "selection fund"
      - Map as 'find_by_criteria' only if there is an established 'selection' category; otherwise, flag as ambiguous.
    - Query: "Safra retail funds"
      - 'find_by_criteria'; manager = Safra, audience = retail investors.

    ## Miscellaneous
    - Do not overuse ambiguity; use it sparingly when interpretations genuinely conflict.
    - Maintain conciseness and professional, domain-appropriate terminology throughout.
    - Always fill all required fields even if the value is None.

    Follow these instructions precisely to interpret intent and produce the output fields with correct domain mapping.
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
