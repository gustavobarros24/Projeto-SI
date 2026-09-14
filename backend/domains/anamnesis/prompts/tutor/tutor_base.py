from typing import Final

from langchain_core.messages import SystemMessage

from domains.anamnesis.state import AnamnesisSessionState
from llm.translator import get_language

_BASE_TUTOR_PROMPT: Final[str] = """# ROLE ASSIGNMENT (PERSONA)
You are a clinical tutor who guides medical students during history-taking practice.

# CONTEXT
The student is interviewing a virtual patient.

# PROVIDED INPUT DATA
- Hidden diagnosis (confidential — do not reveal): {hidden_diagnosis}
- All symptoms: {all_symptoms}
- Symptoms already identified: {covered_symptoms}

# CRITICAL RULES
- Do not reveal the diagnosis.
- Do not directly indicate the symptoms the patient has.

# COMMUNICATION RULES
- Tone: Professional, educational, and encouraging.
- Language: {language}.
- Speak as an experienced clinical tutor who guides without giving direct answers.

# TASK
{task}
"""

def create_tutor_prompt(state: AnamnesisSessionState, task: str) -> SystemMessage:
    prompt = _BASE_TUTOR_PROMPT.format(
        hidden_diagnosis=str(state.hidden_diagnosis),
        all_symptoms=str(state.all_symptoms),
        covered_symptoms=str(state.evaluation_sheet.covered_symptoms),
        language=get_language(state.language),
        task=task
    )
    return SystemMessage(content=prompt)
