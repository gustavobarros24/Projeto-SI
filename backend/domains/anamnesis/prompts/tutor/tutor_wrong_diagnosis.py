from domains.anamnesis.state import AnamnesisSessionState
from domains.anamnesis.prompts.tutor.tutor_base import create_tutor_prompt

from langchain_core.messages import SystemMessage, HumanMessage

def create_wrong_diagnosis_tutor_system_prompt(state: AnamnesisSessionState) -> SystemMessage:
    task = f"""
Your task is to:
- Gently indicate that the diagnosis is not correct
- Encourage the student to re-evaluate the available clinical data
- Guide clinical reasoning towards inconsistencies or gaps in the proposed hypothesis
- Suggest revisiting relevant signs, symptoms, and clinical patterns
- Stimulate critical thinking without ever revealing the correct diagnosis

Rules:
- Do not reveal the true diagnosis
- Do not explicitly list the patient's symptoms
- Maintain a pedagogical and constructive tone
"""
    return create_tutor_prompt(state, task)

def create_wrong_diagnosis_tutor_user_prompt(state: AnamnesisSessionState) -> HumanMessage:
    student_diagnosis = state.diagnosis_attempts[-1]
    content = f"""
<student_diagnosis>
{student_diagnosis}
</student_diagnosis>
"""
    return HumanMessage(content=content)
