from langchain_core.messages import SystemMessage, HumanMessage

from domains.anamnesis.state import AnamnesisSessionState
from utils.messages import get_last_human_message


def create_router_system_prompt(state: AnamnesisSessionState) -> SystemMessage:
    return SystemMessage(content=f"""# ROLE ASSIGNMENT (PERSONA)
You are a message classifier in a medical history-taking session.

# PROVIDED INPUT DATA
- Patient: {state.patient_persona}
- Diagnosis: {state.hidden_diagnosis}
- Symptoms: {state.all_symptoms}

# REQUIRED OUTPUT FORMAT
Respond only with the classification.
""")

def create_router_user_prompt(state: AnamnesisSessionState) -> HumanMessage:
    last_question = get_last_human_message(state.messages)
    content = f"""
<student_question>
{last_question}
</student_question>
"""
    return HumanMessage(content=content)
