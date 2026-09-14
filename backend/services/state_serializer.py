def _serialize_message(msg) -> dict:
    if isinstance(msg, dict):
        data = {
            "role": msg.get("type"),
            "content": msg.get("content"),
            "source": msg.get("name"),
        }
        kwargs = msg.get("additional_kwargs") or {}
    else:
        data = {
            "role": msg.type,
            "content": msg.content,
            "source": getattr(msg, "name", None),
        }
        kwargs = getattr(msg, "additional_kwargs", None) or {}

    sources = kwargs.get("source_documents")
    if sources:
        data["source_documents"] = sources
    audio_id = kwargs.get("audio_id")
    if audio_id:
        data["audio_id"] = audio_id
    return data


def _as_dict(obj):
    return obj.model_dump() if hasattr(obj, "model_dump") else obj


def _findings_of(eval_sheet) -> list[dict]:
    """Normalize an evaluation_sheet (pydantic or dict) into its findings dicts."""
    data = _as_dict(eval_sheet)
    if not isinstance(data, dict):
        return []
    return [d for f in (data.get("findings") or []) if isinstance(d := _as_dict(f), dict)]


def _flatten_final_report(report) -> dict | None:
    if report is None:
        return None
    if hasattr(report,"model_dump"):
        report = report.model_dump()
    if not isinstance(report,dict):
        return report
    report = dict(report)
    feedback = report.pop("feedback",None) or {}
    if hasattr(feedback,"model_dump"):
        feedback = feedback.model_dump()
    return {**report,**feedback}


# Fields that hold case-truth (diagnosis, full symptom list, internal grading
# state) and must NEVER leak to the student during an in-progress session. The
# final report intentionally surfaces some of these for the post-session
# reveal — that path goes through _flatten_final_report and is unaffected.
_HIDDEN_SESSION_FIELDS = frozenset({
    "hidden_diagnosis",
    "all_symptoms",
    "case_info",
    "patient_emotional_state",
    "evaluation_sheet",
    "impression",
})

_EXCLUDED_FROM_SESSION = _HIDDEN_SESSION_FIELDS | {"messages", "diagnosis_attempts"}


def serialize_state(state: dict, module: str | None = None) -> dict:
    max_attempts = state.get("max_diagnosis_attempts", 3)
    attempts_made = len(state.get("diagnosis_attempts", []))

    session = {k: v for k, v in state.items() if k not in _EXCLUDED_FROM_SESSION}
    if module is not None:
        session["module"] = module
    session["diagnosis_attempts_total"] = max_attempts
    session["diagnosis_attempts_remaining"] = max(0, max_attempts - attempts_made)
    session["final_report"] = _flatten_final_report(session.get("final_report"))

    if module == "radiology":
        findings = _findings_of(state.get("evaluation_sheet"))
        session["student_findings"] = [f["finding"] for f in findings if f.get("is_correct")]
        session["incorrect_findings"] = [f["finding"] for f in findings if not f.get("is_correct")]
        session["consecutive_error_count"] = state.get("consecutive_irrelevant_count", 0)

    return {
        "messages": [_serialize_message(m) for m in state.get("messages", [])],
        "session": session,
    }
