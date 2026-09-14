import logging
import uuid

from llm.config import Config
from domains.xray.state import XRaySessionState
from domains.xray.case_repository import get_case
from utils.helpers import node

log = logging.getLogger(__name__)


@node(XRaySessionState)
def interpreter(state: XRaySessionState) -> XRaySessionState:
    # Load the ground truth the teacher reviewed at upload time (snapshot into
    # state — no live MedGemma call, fast start). Later edits or deletions of
    # the case row do NOT affect this session.
    if not state.radiology_case_id:
        raise ValueError("Radiology session requires a radiology_case_id.")
    case = get_case(uuid.UUID(state.radiology_case_id))
    if case is None:
        raise ValueError(f"Radiology case {state.radiology_case_id} not found in database.")
    state.ground_truth_findings = list(case.ground_findings or [])
    state.impression = case.impression
    state.image_url = f"{Config.PUBLIC_BASE_URL}/radiology-cases/{state.radiology_case_id}/file"
    log.info(
        "[interpreter] loaded case %s (%d findings) — skipping live analysis",
        state.radiology_case_id,
        len(state.ground_truth_findings),
    )
    return state
