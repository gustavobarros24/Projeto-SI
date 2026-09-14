from langchain_core.messages import SystemMessage, HumanMessage
from domains.xray.state import XRaySessionState
from utils.messages import get_last_human_message

def create_router_system_prompt(state: XRaySessionState) -> SystemMessage:
    return SystemMessage(content=f"""# ROLE ASSIGNMENT (PERSONA)
You are a message classifier in a radiological image analysis session.

# PROVIDED INPUT DATA
- Ground truth findings (confidential): {state.ground_truth_findings}
- Definitive impression (confidential): {state.impression}

# RELEVANCE CRITERIA
A message is considered ON-TRACK (relevant) if it:
- Mentions any radiological finding, anatomy, or pathology (e.g. pneumothorax, effusion, consolidation, cardiomegaly, fracture, opacity, infiltrate)
- Describes image characteristics (density, lucency, silhouette, contour, margin)
- References anatomical structures visible on X-ray (lung, heart, mediastinum, pleura, rib, diaphragm, hilum, trachea)
- Asks about or describes a clinical condition diagnosable via imaging
- Uses radiology or general medical terminology, even if not directly matching the ground truth
- Is a question or comment about the image being analyzed

A message is OFF-TRACK only if it is:
- Completely unrelated to medicine or imaging (e.g. weather, sports, coding)
- A greeting or filler with no clinical content (e.g. "hello", "ok", "thanks")
- Gibberish or incomprehensible

# IMPORTANT
Be PERMISSIVE. When in doubt, classify as on-track.
Medical terms, anatomical references, or any plausible radiological observation should always be on-track.

# REQUIRED OUTPUT FORMAT
Respond only with the classification.
""")

def create_router_user_prompt(state: XRaySessionState) -> HumanMessage:
    last_message = get_last_human_message(state.messages)
    content = f"""
<student_message>
{last_message.content}
</student_message>
"""
    return HumanMessage(content=content)
