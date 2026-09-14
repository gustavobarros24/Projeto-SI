from typing import Final

from domains.xray.state import XRaySessionState
from llm.translator import Language, get_language

from langchain_core.messages import SystemMessage

_BASE_EVALUATOR_PROMPT: Final[str] = """# ROLE (PERSONA)
You are a performance evaluator for medical students practicing radiological image analysis.

# INPUT DATA
- Ground truth findings: {ground_truth_findings}
- Definitive impression: {impression}

# OBJECTIVE
Assess the quality of the student's performance in the context of clinical history-taking.

# CRITICAL RULES
- Do not reveal the findings.
- Do not directly indicate findings that have not yet been revealed.
- Do not invent information outside the provided context.

# COMMUNICATION RULES
- Tone: Objective, constructive, and educational.
- Language: {language}.

# TASK
{task}
"""

def create_evaluator_prompt(state: XRaySessionState, task: str) -> SystemMessage:
    prompt = _BASE_EVALUATOR_PROMPT.format(
        ground_truth_findings=str(state.ground_truth_findings),
        impression=state.impression,
        language=get_language(Language.EN),
        task=task
    )
    return SystemMessage(content=prompt)

