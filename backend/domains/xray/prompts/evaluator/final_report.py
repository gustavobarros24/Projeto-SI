from langchain_core.messages import SystemMessage, HumanMessage

from domains.xray.prompts.evaluator.evaluate_base import create_evaluator_prompt
from llm.translator import get_language
from domains.xray.state import XRaySessionState
from utils.helpers import MAX_HISTORY_MSGS
from utils.messages import get_last_n_human_messages
from core.evaluator import Grade

def create_final_report_system_prompt(
    state: XRaySessionState,
    total_points: int,
    grade: Grade,
) -> SystemMessage:
    task = f"""
Your task is to generate a final assessment report for the radiological image analysis session.

You should:
- Evaluate the student's overall performance in identifying radiological findings
- Assess the accuracy and completeness of the findings reported
- Evaluate the quality of the final impression
- Identify missed findings and incorrect findings
- Highlight correctly identified findings as strengths
- Provide concrete recommendations for improvement

Session data:
- Ground truth findings: {state.ground_truth_findings}
- Definitive impression: {state.impression}
- Total points: {total_points}
- Grade: {grade}
- Correct findings identified: {state.student_correct_findings}
- Incorrect findings reported: {state.student_incorrect_findings}
- Impressions by the student: {state.student_impressions}
"""
    return create_evaluator_prompt(state, task)

def create_final_report_user_prompt(state: XRaySessionState) -> HumanMessage:
    question_asked = get_last_n_human_messages(state.messages, MAX_HISTORY_MSGS)
    content = f"""
<questions_asked>
{question_asked}
</question_asked>

<impresson_attempts>
{state.impression_attempts}
</impression_attempts>
"""
    return HumanMessage(content=content)
