from langchain_core.messages import SystemMessage, HumanMessage

from domains.anamnesis.prompts.evaluator.evaluate_base import create_evaluator_prompt
from domains.anamnesis.state import AnamnesisSessionState


def create_evaluate_diagnosis_system_prompt(state: AnamnesisSessionState) -> SystemMessage:
    task = f"""
Your task is to evaluate a student's proposed diagnosis in a clinical interview.
You must determine whether the student's diagnosis matches the hidden ground truth diagnosis.

# STEP 1 — NORMALIZATION (CRITICAL)
- Normalize BOTH:
  - hidden diagnosis
  - student diagnosis
into a SHORT standard clinical term.
- Remove language differences 
- Remove wording differences 
- Ignore qualifiers like "suspected", "possible", "probable".

# STEP 2 — EQUIVALENCE CHECK (STRICT)
Mark EXACT if:
- Both refer to the SAME disease entity
- Synonyms, abbreviations, and translations are considered identical
- Differences in wording do NOT change clinical meaning

# STEP 3 — CLASSIFICATION (ONLY AFTER STEP 2)

Evaluate the student's diagnosis attempt against the hidden diagnosis.
Accuracy scale — pick the HIGHEST that applies:
- EXACT (4): Same diagnosis, including common synonyms or abbreviations
- SAME_DISEASE_GROUP (3): Correct organ system / disease category but not specific enough
- RELATED (2): Plausible differential, shares key symptoms but wrong diagnosis
- UNRELATED (1): No meaningful clinical connection

# CRITICAL RULES:
- Hidden diagnosis is the only ground truth.
- NEVER downgrade a correct diagnosis due to language or phrasing differences.
- NEVER use symptom alignment to override diagnosis correctness.
- Do NOT perform general clinical reasoning unless STEP 2 fails.
- Be strict and deterministic.
"""
    return create_evaluator_prompt(state, task)

def create_evaluate_diagnosis_user_prompt(state: AnamnesisSessionState) -> HumanMessage:
    student_diagnosis = state.diagnosis_attempts[-1]
    content = f"""
<student_diagnosis>
{student_diagnosis}
</student_diagnosis>
"""
    return HumanMessage(content=content)
