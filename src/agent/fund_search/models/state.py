from typing import Any

from pydantic import BaseModel, Field


class ConversationState(BaseModel):
    """
    Track multi-turn conversation state.
    Persists context across interactions.
    """

    turn: int = 0
    accumulated_criteria: dict[str, Any] = Field(default_factory=dict)
    last_cnpjs: list[str] = Field(default_factory=list)  # Changed from last_results
    last_query: str = ""
    history: list[dict[str, str]] = Field(default_factory=list)

    # Flags for conversation flow
    awaiting_clarification: bool = False
    awaiting_selection: bool = False  # User needs to pick from options (disambiguation)

    # Store pending intents when awaiting clarification
    pending_intents: list[str] = Field(default_factory=list)

    def merge_criteria(self, new_criteria: dict[str, Any]) -> None:
        """Merge new criteria with accumulated ones."""
        for key, value in new_criteria.items():
            if value is not None:
                self.accumulated_criteria[key] = value

    def clear(self) -> None:
        """Reset state."""
        self.turn = 0
        self.accumulated_criteria = {}
        self.last_cnpjs = []
        self.last_query = ""
        self.history = []
        self.awaiting_clarification = False
        self.awaiting_selection = False
        self.pending_intents = []
