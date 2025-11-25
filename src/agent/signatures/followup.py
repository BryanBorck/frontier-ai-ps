from typing import Literal

import dspy


class FollowUpSignature(dspy.Signature):
    """
    Generate a natural, context-aware follow-up question for a Brazilian Investment Fund Search Agent.

    Context:
    The user is searching for investment funds in Brazil (e.g., "find FIDC funds", "funds from Itau", "funds with high returns").
    If the query is too vague (e.g., "help", "funds"), you must ask a clarifying question to narrow down the search.

    Consider:
    - What the user already specified (or didn't specify)
    - Key criteria to ask for: Fund Type (FI, FIP, FIDC), Manager (Itau, Bradesco), Asset Class (Equity, Fixed Income), or Performance.
    - Natural conversation flow.
    - Language: Reply in Portuguese if the user spoke Portuguese (detected 'pt'), otherwise English.

    Examples of good follow-ups:
    - "Você gostaria de buscar fundos por gestor (ex: Itaú, Vinci) ou por tipo de ativo (ex: Ações, Renda Fixa)?"
    - "Are you looking for specific fund types like FIDC or FII, or generalized mutual funds?"
    """

    query: str = dspy.InputField(desc="User's original query")

    parsed_so_far: str = dspy.InputField(desc="JSON string of what criteria we already extracted")

    result_count: int = dspy.InputField(desc="How many results found (0 if not searched yet)")

    user_language: Literal["pt", "en"] = dspy.InputField(desc="Detected language of user's query")

    follow_up_question: str = dspy.OutputField(
        desc="Natural follow-up question to clarify user intent"
    )

    suggested_options: list[str] = dspy.OutputField(
        desc="2-3 quick options user can choose from (e.g. 'Buscar por Gestor', 'Melhores Retornos')"
    )
