from typing import Any, Final, Optional

from pydantic import BaseModel, Field

from llm.translator import Language
from utils.messages import Message

_MAX_ATTEMPTS: Final[int] = 3

class Feedback(BaseModel):
    strengths: list[str] = Field(
        ..., description="List of 2-3 concrete strengths."
    )
    improvements: list[str] = Field(
        ..., description="List of 2-3 specific areas to improve."
    )
    overall_feedback: str = Field(
        ..., description="3-4 sentence paragraph of overall constructive feedback."
    )

class FinalReport(BaseModel):
    feedback: Feedback
    total_points: int
    max_points: int
    grade: str
    source_documents: list[dict] = Field(default_factory=list)

class ChatSessionState(BaseModel):
    messages: list[Message] = Field(default_factory=list)
    language: Language

    turn_count: int = 0
    route_decision: str = ""
    session_summary: str = ""
    case_info: str = ""
    consecutive_irrelevant_count: int = 0

    max_attempts: int = _MAX_ATTEMPTS
    gave_up: bool = False
    last_input_was_attempt: bool = False

    final_report: Optional[Any] = None

