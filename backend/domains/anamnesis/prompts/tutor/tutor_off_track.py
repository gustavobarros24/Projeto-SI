from langchain_core.messages import SystemMessage, HumanMessage

from domains.anamnesis.state import AnamnesisSessionState
from domains.anamnesis.prompts.tutor.tutor_base import create_tutor_prompt

from utils.messages import get_last_n_human_messages
from utils.helpers import MAX_HISTORY_MSGS

def create_off_track_tutor_system_prompt(state: AnamnesisSessionState) -> SystemMessage:
    task = """
The student is deviating from clinically relevant reasoning for the likely diagnosis.

Your task is to:
- Gently indicate that the clinical reasoning is not well focused
- Help the student refocus on a more relevant line of questioning for the diagnosis
- Implicitly suggest more useful clinical domains to explore (without revealing the diagnosis or specific symptoms)
- Encourage structured clinical reasoning and hypothesis-driven thinking

If possible, guide them toward a more appropriate next question.
"""
    return create_tutor_prompt(state, task)


def create_off_track_tutor_user_prompt(state: AnamnesisSessionState) -> HumanMessage:
    last_questions = get_last_n_human_messages(state.messages, MAX_HISTORY_MSGS)
    content = f"""
<student_questions>
{last_questions}
</student_questions>
"""
    return HumanMessage(content=content)
