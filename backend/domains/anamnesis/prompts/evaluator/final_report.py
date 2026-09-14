from langchain_core.messages import SystemMessage, HumanMessage

from domains.anamnesis.prompts.evaluator.evaluate_base import create_evaluator_prompt
from domains.anamnesis.state import AnamnesisSessionState
from llm.translator import get_language
from utils.helpers import MAX_HISTORY_MSGS
from utils.messages import get_last_n_human_messages
from core.evaluator import Grade

def create_final_report_system_prompt(
    state: AnamnesisSessionState,
    total_points: int,
    grade: Grade,
) -> SystemMessage:
    task = f"""
Your task is to generate a final assessment report for the clinical history-taking session.

You should:
- Evaluate the student's overall performance
- Analyse the quality of the questions (clarity, relevance, logical progression)
- Assess efficiency in collecting key symptoms
- Evaluate diagnostic reasoning throughout the session
- Identify critical errors and important gaps
- Highlight strengths
- Provide concrete recommendations for improvement

Consider:
- Questions asked by the student
- Diagnostic attempts
- Symptoms that were (or were not) identified

Session data:
- Disease diagnosis: {state.hidden_diagnosis}
- Total symptoms: {state.all_symptoms}
- Total points: {total_points}
- Grade: {grade}
- Covered symptoms by the student: {state.student_covered_symptoms}
- Diagnosis attempts by the student: {state.student_diagnosis}

# RULES
Language: {get_language(state.language)}
"""
    return create_evaluator_prompt(state, task)

def create_final_report_user_prompt(state: AnamnesisSessionState) -> HumanMessage:
    question_asked = get_last_n_human_messages(state.messages, MAX_HISTORY_MSGS)
    content = f"""
<questions_asked>
{question_asked}
</question_asked>

<diagnosis_attempts>
{state.diagnosis_attempts}
</diagnosis_attempts>
"""
    return HumanMessage(content=content)
