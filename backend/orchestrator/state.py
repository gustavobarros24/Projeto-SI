from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from llm.translator import Language
from utils.messages import Message


class SessionType(str, Enum):
    RADIOLOGY = "radiology"
    ANAMNESIS = "anamnesis"

class StudentProfile(BaseModel):
    student_id: str
    name: str = Field(..., description="Student's name.")
    radiology_level: int = Field(
        ...,
        description="Student's level of knowledge in the radiology module, from 1 to 5.",
    )
    anamnesis_level: int = Field(
        ...,
        description="Student's level of knowledge in the anamnesis module, from 1 to 5.",
    )
    radiology_sessions: int = Field(
        ...,
        description="Number of radiology study sessions completed by the student.",
    )
    anamnesis_sessions: int = Field(
        ...,
        description="Number of anamnesis study sessions completed by the student.",
    )
    weak_areas: List[str] = Field(
        ...,
        description="Areas of knowledge in which the student has the most difficulty.",
    )

class OrchestratorState(BaseModel):
    messages: list[Message] = Field(default_factory=list)
    student_id: str = ""
    language: Language = Language.EN
    loaded_student_weak_areas: list[str] = Field(default_factory=list)
    student_profile: Optional[StudentProfile] = None
    module: Optional[SessionType] = Field(
        None, description="Current study module for the student's session."
    )
    case_info: str = ""
    image_url: str = ""
    anamnesis_case_id: Optional[str] = None
    radiology_case_id: str = ""
    session_summary: str = ""
    final_report: Optional[dict[str,Any]] = None
