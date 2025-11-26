from typing import Literal

from pydantic import BaseModel, Field


class SearchOutput(BaseModel):
    """
    Output of the Fund Search Agent.
    """
    cnpjs: list[str] = Field(default_factory=list, description="List of discovered/filtered CNPJs")
    
    # Context flags for the next step (Response Generation)
    response_type: str = Field(..., description="Type of response (single_match, list_results, no_results, disambiguation, etc.)")
    interpretation_note: str | None = Field(None, description="Note explaining how the query was interpreted")
    
    # Ambiguity handling
    is_ambiguous: bool = Field(False, description="Whether the query result is ambiguous")
    
    # Conversation handling
    suggested_followup: str | None = None
    suggestions: list[str] = Field(default_factory=list)
    detected_language: str = "pt"
