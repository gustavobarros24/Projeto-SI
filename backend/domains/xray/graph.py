import logging

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from domains.xray.state import XRaySessionState
from domains.xray.evaluator import XRayEvaluator
from domains.xray.tutor import XRayTutor
from domains.xray.router import RouteDecision, router
from domains.xray.interpreter import interpreter
from domains.xray.presenter import presenter
from utils.helpers import node
from utils.messages import build_input_message

log = logging.getLogger(__name__)

evaluator = XRayEvaluator()
tutor = XRayTutor()

@node(XRaySessionState)
def await_input(state: XRaySessionState) -> XRaySessionState:
    user_input = interrupt("awaiting_student_input")
    if isinstance(user_input, dict):
        input_type = user_input.get("type")
        if input_type == "give_up":
            log.info("[await_input] GIVE_UP")
            state.gave_up = True
            state.last_input_was_attempt = False
        elif user_input.get("is_diagnosis"):
            message = build_input_message(user_input["content"])
            state.impression_attempts.append(message)
            state.last_input_was_attempt = True
            message.name = "diagnosis"
            state.messages.append(message)
            log.info(f"[await_input] IMPRESSION → impression_attempts (total: {len(state.impression_attempts)}): '{message.content}'...")
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


def build_xray_graph():
    log.info("Starting xray graph...")
    graph = StateGraph(XRaySessionState)

    graph.add_node("interpreter", interpreter)
    graph.add_node("presenter", presenter)
    graph.add_node("await_input", await_input)
    graph.add_node("router", router)
    graph.add_node("tutor_off_track", tutor.tutor_off_track)
    graph.add_node("tutor_response", tutor.tutor_response)
    graph.add_node("tutor_wrong_impression", tutor.tutor_wrong_impression)
    graph.add_node("evaluate_input", evaluator.evaluate_input)
    graph.add_node("evaluate_impression", evaluator.evaluate_impression)
    graph.add_node("final_report", evaluator.generate_final_report)

    graph.add_edge(START, "interpreter")
    graph.add_edge("interpreter", "presenter")
    graph.add_edge("presenter", "await_input")
    graph.add_edge("await_input", "router")

    graph.add_conditional_edges(
        "router",
        lambda state: state.route_decision,
        {
            RouteDecision.TUTOR_OFF_TRACK: "tutor_off_track",
            RouteDecision.TUTOR_RESPONSE: "evaluate_input",
            RouteDecision.TUTOR_WRONG_IMPRESSION: "tutor_wrong_impression",
            RouteDecision.EVALUATE_IMPRESSION: "evaluate_impression",
            RouteDecision.FINAL_REPORT: "final_report",
        },
    )

    graph.add_conditional_edges(
        "evaluate_input",
        lambda state: state.route_decision,
        {
            RouteDecision.TUTOR_OFF_TRACK: "tutor_off_track",
            RouteDecision.TUTOR_RESPONSE: "tutor_response",
        },
    )

    graph.add_conditional_edges(
        "evaluate_impression",
        lambda state: state.route_decision,
        {
            RouteDecision.TUTOR_WRONG_IMPRESSION: "tutor_wrong_impression",
            RouteDecision.FINAL_REPORT: "final_report",
        },
    )

    graph.add_edge("tutor_off_track", "await_input")
    graph.add_edge("tutor_response", "await_input")
    graph.add_edge("tutor_wrong_impression", "await_input")
    graph.add_edge("final_report", END)

    return graph.compile()
