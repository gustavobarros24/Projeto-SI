from langchain_core.messages import SystemMessage, HumanMessage

from domains.xray.state import XRaySessionState
from domains.xray.prompts.tutor.tutor_base import create_tutor_prompt

from utils.messages import get_last_n_human_messages
from utils.helpers import MAX_HISTORY_MSGS

def create_off_track_tutor_system_prompt(state: XRaySessionState) -> SystemMessage:
    task = """
The student is reporting findings that are not clinically relevant or is deviating from structured radiological analysis.
Your task is to:
- Gently indicate that the current observations are not well focused
- Help the student refocus on a more systematic approach to image analysis
- Implicitly suggest more relevant anatomical regions or radiological features to examine (without revealing specific findings)
- Encourage structured radiological reasoning, such as reviewing the image systematically by region
If possible, guide them toward a more appropriate next observation.
"""
    return create_tutor_prompt(state, task)

def create_off_track_tutor_user_prompt(state: XRaySessionState) -> HumanMessage:
    last_messages = get_last_n_human_messages(state.messages, MAX_HISTORY_MSGS)
    content = f"""
<student_messages>
{last_messages}
</student_messages>
"""
    return HumanMessage(content=content)
