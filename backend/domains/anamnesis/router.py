import logging

from enum import Enum

from core.router import RouterOutput, ContextType
from domains.anamnesis.state import AnamnesisSessionState
from domains.anamnesis.prompts.router import create_router_system_prompt, create_router_user_prompt
from utils.helpers import node
from llm.models import create_llm
from llm.config import Config


log = logging.getLogger(__name__)

class RouteDecision(str, Enum):
    PATIENT = "patient"
    TUTOR_OFF_TRACK = "tutor_off_track"
    TUTOR_WRONG_DIAGNOSIS = "tutor_wrong_diagnosis"
    FINAL_REPORT = "final_report"
    EVALUATE_DIAGNOSIS = "evaluate_diagnosis"


@node(AnamnesisSessionState)
def router(state: AnamnesisSessionState) -> AnamnesisSessionState:
    log.info("Starting router anamnesis...")
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
        log.info("Diagnosis input detected: routing to evaluate_diagnosis...")
        state.route_decision = RouteDecision.EVALUATE_DIAGNOSIS
        return state

    elif context == ContextType.IRRELEVANT:
        # TODO: censor non medical questions
        log.info("Context irrelevant...")
        state.route_decision = RouteDecision.PATIENT
        return state

    elif context == ContextType.RELEVANT:
        log.info("Context relevant...")
        state.route_decision = RouteDecision.PATIENT

        return state
    else:
        log.error("Context not defined...")
        raise Exception("Error detecting type of question.")
