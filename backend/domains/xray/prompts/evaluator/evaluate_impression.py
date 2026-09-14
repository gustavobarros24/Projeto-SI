from langchain_core.messages import SystemMessage, HumanMessage

from domains.xray.prompts.evaluator.evaluate_base import create_evaluator_prompt
from domains.xray.state import XRaySessionState

def create_evaluate_impression_system_prompt(state: XRaySessionState) -> SystemMessage:
    task = """
Your task is to evaluate the student's radiological impression against the ground truth impression.

Evaluate the impression semantically and clinically, not by exact wording.

Classify the student's impression using the following rubric:

- EXACT_MATCH (5):
  The student impression matches the ground truth diagnosis and major findings.

- CLINICALLY_EQUIVALENT (4):
  Different wording but essentially the same clinical meaning and interpretation.

- PARTIAL_MATCH (3):
  The student identified the correct disease process or several major findings,
  but the impression is incomplete or missing important components.

- LIMITED_MATCH (2):
  The student identified at least one correct relevant finding,
  but missed the main diagnosis or overall interpretation.

- MINIMAL_RELEVANCE (1):
  The student impression has weak or nonspecific overlap with the ground truth.

- UNRELATED (0):
  The student impression is clinically unrelated or contradicts the ground truth.

Important rules:
- Partial overlap is NOT unrelated.
- If the student correctly identifies any important finding from the ground truth,
  the classification should usually be at least LIMITED_MATCH.
- Do not require identical wording.
- The student may describe findings instead of the final diagnosis.
- Missing findings should lower the score but should not force UNRELATED.
- Choose the HIGHEST applicable category.
- Base the evaluation strictly on semantic and clinical similarity.

You should return:
- the interpreted student impression
- the selected accuracy classification
- brief reasoning explaining the classification
"""
    return create_evaluator_prompt(state, task)

def create_evaluate_impression_user_prompt(state: XRaySessionState) -> HumanMessage:
    student_impression = state.impression_attempts[-1]
    content = f"""
<student_impression>
{student_impression}
</student_impression>
"""
    return HumanMessage(content=content)
