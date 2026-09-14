from langchain_core.messages import SystemMessage, HumanMessage

from domains.anamnesis.prompts.evaluator.evaluate_base import create_evaluator_prompt
from domains.anamnesis.state import AnamnesisSessionState
from utils.messages import get_last_human_message

def create_evaluate_question_system_prompt(state: AnamnesisSessionState) -> SystemMessage:
    task = f"""
Evaluate the student's question in the context of clinical history-taking.

Assess the following dimensions:
- Clinical relevance to the case
- Clarity and specificity
- Redundancy with previous questions
- Appropriateness of sequencing within the interview

OUTPUT RULES:
- symptom_targeted: copy the exact symptom name from all_symptoms (e.g. "chest pain"). Max 5 words, no explanation, no parentheses, no reasoning. Null if the question does not target a specific listed symptom.
- Do not reveal the diagnosis.
- Do not hint at symptoms not yet uncovered.
- Base evaluation only on the provided information.
"""
    return create_evaluator_prompt(state, task)

def create_evaluate_question_user_prompt(state: AnamnesisSessionState) -> HumanMessage:
    last_question = get_last_human_message(state.messages)
    content = f"""
<student_question>
{last_question}
</student_question>
"""
    return HumanMessage(content=content)
