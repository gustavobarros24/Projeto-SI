import logging

from enum import Enum

from core.router import RouterOutput, ContextType
from llm.config import Config
from llm.models import create_llm
from domains.xray.state import XRaySessionState
from domains.xray.prompts.router import create_router_system_prompt, create_router_user_prompt
from utils.helpers import node

log = logging.getLogger(__name__)

class RouteDecision(str, Enum):
    TUTOR_OFF_TRACK = "tutor_off_track"
    TUTOR_WRONG_IMPRESSION = "tutor_wrong_impression"
    TUTOR_RESPONSE = "tutor_reponse"
    FINAL_REPORT = "final_report"
    EVALUATE_IMPRESSION = "evaluate_impression"

@node(XRaySessionState)
def router(state: XRaySessionState) -> XRaySessionState:
    log.info("Starting router xray...")
    system_prompt = create_router_system_prompt(state)
    user_prompt = create_router_user_prompt(state)

    chat_llm = create_llm(Config.CHAT_MODEL)
    classifier = chat_llm.with_structured_output(RouterOutput)
    result: RouterOutput = classifier.invoke([system_prompt, user_prompt])

    context = result.context
    log.info(f"Router context: {context}...")

    state.turn_count += 1
    if state.gave_up:
        log.info("Student gave up student: routing to final report...")
        state.route_decision = RouteDecision.FINAL_REPORT
        return state

    if state.last_input_was_attempt:
        log.info("Impression input detected: routing to impression...")
        state.route_decision = RouteDecision.EVALUATE_IMPRESSION
        return state

    elif context == ContextType.IRRELEVANT:
        # TODO: censor non medical questions
        log.info("Context irrelevant...")
        state.route_decision = RouteDecision.TUTOR_RESPONSE
        return state

    elif context == ContextType.RELEVANT:
        log.info("Context relevant...")
        state.route_decision = RouteDecision.TUTOR_RESPONSE
        return state
    else:
        log.error("Context not defined...")
        raise Exception("Error detecting type of question.")

