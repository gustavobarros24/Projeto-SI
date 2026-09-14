from langchain_core.messages import SystemMessage, HumanMessage

from domains.xray.prompts.evaluator.evaluate_base import create_evaluator_prompt
from domains.xray.state import XRaySessionState
from utils.messages import get_last_human_message

def create_evaluate_finding_system_prompt(state: XRaySessionState) -> SystemMessage:
    task = """
Your task is to evaluate the student's message and determine if it describes a radiological finding.

You should:
- Identify whether the message contains a radiological finding
- Extract and NORMALIZE the finding to a SHORT standard clinical/radiological term only
- The finding field must be ONLY the clinical term, no explanations, no parentheses, no additional context.
- Compare it against the ground truth findings
- Classify it as correct or incorrect

Relevance rules — mark is_relevant=True if the message:
- Contains ANY medical, anatomical, or radiological term, even colloquial or informal ones
- Describes a symptom, condition, or structure visible on X-ray
- Is a question or observation about the image, even if vague or imprecise
- Uses non-English terms that map to radiological concepts

Mark is_relevant=False ONLY if the message:
- Has zero medical or anatomical content (e.g. "ok", "hello", unrelated topics)
- Is pure gibberish with no clinical meaning

Additional Rules:
- Normalize colloquial expressions to their clinical equivalent before comparing
- Do not reveal any findings that have not been mentioned by the student
- Do not confirm or deny findings indirectly through your tone or wording
- Base your evaluation strictly on the provided ground truth
- If the message contains no identifiable finding, mark it as not a finding
"""
    return create_evaluator_prompt(state, task)

def create_evaluate_finding_user_prompt(state: XRaySessionState) -> HumanMessage:
    last_message = get_last_human_message(state.messages)
    content = f"""
<student_message>
{last_message}
</student_message>
"""
    return HumanMessage(content=content)
