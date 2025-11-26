from typing import Literal

import dspy


class ResponseSignature(dspy.Signature):
    """
    You are a specialized Investment Fund Assistant.
    Your main goal is to help users search for investment funds and retrieve their details (Name, CNPJ, Type, Class, AUM, etc.).

    Generate a helpful, natural language response based on search results.
    Handles distinct scenarios: explicit matches, list of options, empty results, or disambiguation.

    IMPORTANT:
    - When acting as 'informational', explain your capability to search for funds and provide details.
    - When interpretation_note is provided, ALWAYS end with a follow-up question asking if the user was looking for something else.
    """

    query: str = dspy.InputField(desc="User's original query")

    results_summary: str = dspy.InputField(
        desc="Summary of search results (count, top items, metadata)"
    )

    response_type: Literal[
        "single_match",  # Found exactly one clear match
        "list_results",  # Found a good list (2-20 items)
        "disambiguation",  # Found ambiguous matches requiring user choice
        "no_results",  # No matches found
        "too_many_results",  # Too many matches, asking to narrow down
        "informational",  # Answering a general question (no DB results expected)
    ] = dspy.InputField(desc="The type of response to generate")

    interpretation_note: str | None = dspy.InputField(
        desc="""If provided, the query was potentially ambiguous. 
        Include this interpretation in your response and ASK if user meant something else.
        Example: 'I found Bradesco funds that track gold prices. Were you looking for a fund with a specific name instead?'"""
    )

    user_language: Literal["pt", "en"] = dspy.InputField(
        desc="""Target language for the response.
        - 'en': Respond in English.
        - 'pt': Respond in Portuguese.
        CRITICAL: IGNORE the language of the 'query' or 'results_summary'. 
        You MUST output the 'answer' in the language specified here."""
    )

    answer: str = dspy.OutputField(
        desc="""Natural language response. Include markdown formatting for lists/bold text.
        If 'list_results', list AT LEAST 5-10 items if available, or all of them if the user explicitly asked for 'all' or a high number (e.g. '10 funds').
        Do NOT arbitrarily truncate the list to 3 items if more are available and relevant.
        If interpretation_note is provided, END with a follow-up question about alternative interpretations."""
    )
