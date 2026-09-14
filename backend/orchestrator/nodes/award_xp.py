import logging
import uuid

from auth.models import User
from core.progression import level_for_xp
from orchestrator.state import OrchestratorState, SessionType
from rag.db import SyncSession

log = logging.getLogger(__name__)

_XP_COLUMN = {
    SessionType.ANAMNESIS: ("anamnesis_xp", "anamnesis_level"),
    SessionType.RADIOLOGY: ("radiology_xp", "radiology_level"),
}


def award_xp(state: OrchestratorState):
    """Award the session score as XP once, when a session completes.

    Runs exactly once per session: the orchestrator only reaches this node after a
    subgraph hits END (normal turns stay paused at interrupt()), so no anti-double
    flag is needed.
    """
    if state.session_summary != "ended" or not state.final_report:
        return

    columns = _XP_COLUMN.get(state.module)
    if columns is None:
        return

    points = int(state.final_report.get("total_points", 0) or 0)
    if points <= 0:
        return

    xp_col, level_col = columns
    try:
        student_uuid = uuid.UUID(state.student_id)
    except (ValueError, TypeError):
        log.warning("award_xp: invalid student_id %r", state.student_id)
        return

    with SyncSession() as session:
        user = session.get(User, student_uuid)
        if user is None:
            log.warning("award_xp: user %s not found", state.student_id)
            return
        new_xp = getattr(user, xp_col) + points
        new_level = level_for_xp(new_xp)
        setattr(user, xp_col, new_xp)
        setattr(user, level_col, new_level)
        session.commit()
        log.info(
            "award_xp: student %s +%d xp on %s (xp=%d, level=%d)",
            state.student_id,
            points,
            state.module.value,
            new_xp,
            new_level,
        )
