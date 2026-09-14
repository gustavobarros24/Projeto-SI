from domains.xray.state import XRaySessionState
from domains.xray.prompts.tutor.tutor_base import create_tutor_prompt
from utils.messages import get_last_human_message

from langchain_core.messages import SystemMessage, HumanMessage

def create_response_tutor_system_prompt(state: XRaySessionState) -> SystemMessage:
    task = """
Your task is to give brief feedback on the student's last reported finding.

You should:
- Confirm if the finding is correct and present in the image
- If incorrect, explain why it does not match the radiological evidence without revealing other unidentified findings
- If no finding was identified in the message, indicate that the message did not describe a radiological finding

Rules:
- Do not reveal findings the student has not yet identified
- Do not confirm or deny other findings indirectly
- Keep the feedback concise, one to two sentences maximum
"""
    return create_tutor_prompt(state, task)


def create_response_tutor_response_user_prompt(state: XRaySessionState) -> HumanMessage:
    last_message = get_last_human_message(state.messages)
    content = f"""
<student_message>
{last_message}
</student_message>
"""
    return HumanMessage(content=content)
