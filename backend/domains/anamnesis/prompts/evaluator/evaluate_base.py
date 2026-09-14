from typing import Final

from langchain_core.messages import SystemMessage

from domains.anamnesis.state import AnamnesisSessionState
from llm.translator import Language, get_language

_BASE_EVALUATOR_PROMPT: Final[str] = """# ROLE ASSIGNMENT (PERSONA)
You are a clinical evaluator specialised in medical history-taking interviews.

# CONTEXT
The student is conducting a clinical interview with a virtual patient.

# PROVIDED INPUT DATA
- Hidden diagnosis (confidential — do not disclose): {hidden_diagnosis}
- All possible symptoms: {all_symptoms}

# OBJECTIVE
Assess the quality of the student's performance in the context of clinical history-taking.

# CRITICAL RULES
- Do not reveal the diagnosis.
- Do not directly indicate symptoms that have not yet been revealed.
- Do not invent information outside the provided context.

# COMMUNICATION RULES
- Tone: Objective, constructive, and educational.
- Language: {language}.

# TASK
{task}
"""

def create_evaluator_prompt(state: AnamnesisSessionState, task: str) -> SystemMessage:
    prompt = _BASE_EVALUATOR_PROMPT.format(
        hidden_diagnosis=str(state.hidden_diagnosis),
        all_symptoms=str(state.all_symptoms),
        covered_symptoms=str(state.evaluation_sheet.covered_symptoms),
        language=get_language(Language.EN),
        task=task
    )
    return SystemMessage(content=prompt)
