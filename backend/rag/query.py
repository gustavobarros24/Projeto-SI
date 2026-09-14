from utils.messages import Message, MessageType


def _last_human_text(messages: list) -> str:
    for m in reversed(messages or []):
        msg_type = getattr(m, "type", None) or (m.get("type") if isinstance(m, dict) else None)
        if msg_type in (MessageType.HUMAN, MessageType.HUMAN.value, "human"):
            content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else "")
            return content or ""
    return ""


def build_anamnesis_query(state) -> str:
    last = _last_human_text(state.messages)
    hidden = (state.hidden_diagnosis or "").strip()
    parts = [p for p in (last.strip(), hidden) if p]
    return " ".join(parts)


def build_xray_query(state) -> str:
    last = _last_human_text(state.messages)
    findings = ", ".join(state.ground_truth_findings or [])
    parts = [p for p in (last.strip(), findings) if p]
    return " ".join(parts)


def build_anamnesis_final_report_query(state) -> str:
    diagnoses = " | ".join(state.student_diagnosis or [])
    hidden = (state.hidden_diagnosis or "").strip()
    parts = [p for p in (diagnoses, hidden) if p]
    return " ".join(parts) or _last_human_text(state.messages)


def build_xray_final_report_query(state) -> str:
    impressions = " | ".join(state.student_impressions or [])
    impression = (state.impression or "").strip()
    findings = ", ".join(state.ground_truth_findings or [])
    parts = [p for p in (impressions, impression, findings) if p]
    return " ".join(parts) or _last_human_text(state.messages)
