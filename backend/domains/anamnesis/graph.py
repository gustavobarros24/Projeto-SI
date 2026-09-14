import logging
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from domains.anamnesis.case_repository import get_case
from domains.anamnesis.state import AnamnesisSessionState, PatientPersona
from domains.anamnesis.evaluator import AnamnesisEvaluator
from domains.anamnesis.patient import patient
from domains.anamnesis.tutor import AnamnesisTutor
from domains.anamnesis.router import RouteDecision, router
from domains.anamnesis.presenter import presenter
from utils.helpers import node
from utils.messages import build_input_message

log = logging.getLogger(__name__)

evaluator = AnamnesisEvaluator()
tutor = AnamnesisTutor()


@node(AnamnesisSessionState)
def initialize_session(state: AnamnesisSessionState) -> AnamnesisSessionState:
    if not state.anamnesis_case_id:
        raise ValueError(
            "Anamnesis session started without anamnesis_case_id — a case must be selected."
        )

    case = get_case(uuid.UUID(state.anamnesis_case_id))
    if case is None:
        raise ValueError(f"Anamnesis case {state.anamnesis_case_id} not found in database.")

    # Snapshot the case into state — subsequent edits or deletions of the case
    # row will NOT affect this session, because the checkpointer persists the
    # whole state at every step.
    state.patient_persona = PatientPersona(
        name=case.patient_name,
        age=case.patient_age,
        gender=case.patient_gender,
    )
    state.hidden_diagnosis = case.hidden_diagnosis
    state.all_symptoms = list(case.symptoms or [])
    state.patient_emotional_state = case.patient_emotional_state
    state.consecutive_irrelevant_count = 0

    state.case_info = (
        f"Hidden diagnosis: {state.hidden_diagnosis}\n"
        f"All symptoms: {', '.join(state.all_symptoms)}\n"
        f"Patient persona: {state.patient_persona.name}, "
        f"{state.patient_persona.age} years old, {state.patient_persona.gender}"
    )

    log.info(
        "[initialize_session] loaded case %s (%d symptoms)",
        state.anamnesis_case_id,
        len(state.all_symptoms),
    )
    return state

@node(AnamnesisSessionState)
def await_input(state: AnamnesisSessionState) -> AnamnesisSessionState:
    user_input = interrupt("awaiting_student_input")
    if isinstance(user_input, dict):
        input_type = user_input.get("type")
        if input_type == "give_up":
            log.info("[await_input] GIVE_UP")
            state.gave_up = True
            state.last_input_was_attempt = False
        elif user_input.get("is_diagnosis"):
            message = build_input_message(user_input["content"])
            state.diagnosis_attempts.append(message)
            state.last_input_was_attempt = True
            message.name = "diagnosis"
            state.messages.append(message)
            log.info(f"[await_input] DIAGNOSIS → diagnosis_attempts (total: {len(state.diagnosis_attempts)}): '{message.content}'")
        else:
            # Normal question submitted by voice — carries the recorded audio note.
            message = build_input_message(user_input["content"])
            if user_input.get("audio_id"):
                message.additional_kwargs["audio_id"] = user_input["audio_id"]
            state.messages.append(message)
            state.last_input_was_attempt = False
    else:
        message = build_input_message(user_input)
        state.messages.append(message)
        state.last_input_was_attempt = False
    return state


def build_anamnesis_graph():
    log.info("Starting anamnesis...")
    graph = StateGraph(AnamnesisSessionState)

    graph.add_node("initialize_session", initialize_session)
    graph.add_node("presenter", presenter)
    graph.add_node("await_input", await_input)
    graph.add_node("router", router)
    graph.add_node("patient", patient)
    graph.add_node("tutor_off_track", tutor.tutor_off_track)
    graph.add_node("tutor_wrong_diagnosis", tutor.tutor_wrong_diagnosis)
    graph.add_node("score_question", evaluator.evaluate_input)
    graph.add_node("evaluate_diagnosis", evaluator.evaluate_diagnosis_attempt)
    graph.add_node("final_report", evaluator.generate_final_report)

    graph.add_edge(START, "initialize_session")
    graph.add_edge("initialize_session", "presenter")
    graph.add_edge("presenter", "await_input")
    graph.add_edge("await_input", "router")

    graph.add_conditional_edges(
        "router",
        lambda state: state.route_decision,
        {
            RouteDecision.PATIENT: "score_question",
            RouteDecision.TUTOR_OFF_TRACK: "tutor_off_track",
            RouteDecision.TUTOR_WRONG_DIAGNOSIS: "tutor_wrong_diagnosis",
            RouteDecision.FINAL_REPORT: "final_report",
            RouteDecision.EVALUATE_DIAGNOSIS: "evaluate_diagnosis",
        },
    )
    graph.add_conditional_edges(
        "score_question",
        lambda state: state.route_decision,
        {
            RouteDecision.TUTOR_OFF_TRACK: "tutor_off_track",
            RouteDecision.PATIENT: "patient",
            RouteDecision.FINAL_REPORT: "final_report",
        },
    )
    graph.add_conditional_edges(
        "evaluate_diagnosis",
        lambda state: state.route_decision,
        {
            RouteDecision.TUTOR_WRONG_DIAGNOSIS: "tutor_wrong_diagnosis",
            RouteDecision.FINAL_REPORT: "final_report",
        },
    )

    graph.add_edge("patient", "await_input")
    graph.add_edge("tutor_wrong_diagnosis", "await_input")
    graph.add_edge("tutor_off_track", "await_input")
    graph.add_edge("final_report", END)

    return graph.compile()
