from domains.xray.state import XRaySessionState
from domains.xray.prompts.tutor.tutor_base import create_tutor_prompt

from langchain_core.messages import SystemMessage, HumanMessage

def create_wrong_impression_tutor_system_prompt(state: XRaySessionState) -> SystemMessage:
    task = """
Your task is to:
- Gently indicate that the radiological impression is not correct
- Encourage the student to re-evaluate the findings they have identified so far
- Guide their reasoning towards inconsistencies or gaps between their reported findings and their conclusion
- Suggest revisiting specific radiological features or anatomical regions they may have overlooked
- Stimulate critical thinking without ever revealing the definitive impression

Rules:
- Do not reveal the definitive impression or any information the student has not yet identified about it
- Do not expose findings the student has not yet identified
- Maintain a pedagogical and constructive tone
"""
    return create_tutor_prompt(state, task)


def create_wrong_impression_tutor_user_prompt(state: XRaySessionState) -> HumanMessage:
    student_impression = state.impression_attempts[-1]
    content = f"""
<student_impression>
{student_impression}
</student_impression>
"""
    return HumanMessage(content=content)
