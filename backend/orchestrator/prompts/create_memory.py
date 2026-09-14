from typing import Final

from langchain_core.messages import SystemMessage, HumanMessage

from orchestrator.state import OrchestratorState
from llm.translator import get_language
from utils.messages import MessageType

_CREATE_MEMORY_PROMPT: Final[str] = """You are an expert in medical education analysis. You are observing a clinical practice session between a medical student and a simulation system.
Your task is to analyse the session and update the student's memory profile by identifying their clinical areas of difficulty.

IMPORTANT: Weak areas MUST be exclusively clinical or medical competencies related to the session. Valid examples:
- "exploration of cardiovascular symptoms"
- "open-ended questioning technique"
- "identification of chest pain"
- "differential diagnosis of dyspnoea"
- "communication with an anxious patient"
- "systematic symptom coverage"

DO NOT invent generic academic subjects (e.g. "Science", "Mathematics", "History"). If there is insufficient evidence in the session to identify concrete weak areas, keep existing values or return an empty list.

*SESSION DATA*

Clinical practice module:
{module}

Relevant case or patient information:
{case_info}

Respond with an object containing the following fields:
- student_id: the student's identifier
- weak_areas: list of the student's clinical areas of difficulty

For each field, if there is no new information, keep the existing value. If there is new information, update it.
Language: {language}.
"""

def create_memory_system_prompt(state: OrchestratorState) -> SystemMessage:
    prompt = _CREATE_MEMORY_PROMPT.format(
        module=state.module.value or "",
        case_info=state.case_info,
        language=get_language(state.language),
    )
    return SystemMessage(content=prompt)


def create_memory_user_prompt(state: OrchestratorState, memory_profile) -> HumanMessage:
    # Filtra apenas as mensagens do estudante
    # e formata para uma lista numerada.
    student_messages = "\n".join(
        f"{i}. \"{msg.content}\""
        for i, msg in enumerate(state.messages, 1)
        if msg.type == MessageType.HUMAN
    )
    content = f"""
<student_messages>
{student_messages}
</student_messages>

<memory_profile>
{memory_profile}
</memory_profile>
"""
    return HumanMessage(content=content)
