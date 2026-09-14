import logging

from core.tutor import ITutor
from llm.provider import clean_model_response
from llm.models import create_llm
from llm.config import Config
from domains.xray.state import XRaySessionState
from domains.xray.prompts.tutor.tutor_off_track import create_off_track_tutor_system_prompt, create_off_track_tutor_user_prompt
from domains.xray.prompts.tutor.tutor_wrong_impression import create_wrong_impression_tutor_user_prompt, create_wrong_impression_tutor_system_prompt
from domains.xray.prompts.tutor.tutor_response import create_response_tutor_system_prompt, create_response_tutor_response_user_prompt
from rag.integration import attach_sources, augment_with_rag
from rag.query import build_xray_query
from utils.helpers import node
from llm.models import create_llm, clean_model_response
from llm.config import Config
from utils.messages import build_output_message

log = logging.getLogger(__name__)


class XRayTutor(ITutor[XRaySessionState]):
    @node(XRaySessionState)
    def tutor_off_track(self, state: XRaySessionState) -> XRaySessionState:
        log.info("Starting xray tutor off track...")
        medical_llm = create_llm(Config.MEDICAL_MODEL)
        system_prompt = create_off_track_tutor_system_prompt(state)
        user_prompt = create_off_track_tutor_user_prompt(state)

        system_prompt, sources = augment_with_rag(system_prompt, build_xray_query(state))

        reply = medical_llm.invoke([system_prompt, user_prompt])
        clean_model_response(reply)
        attach_sources(reply, sources)
        message = build_output_message(reply.content)
        message.name = "tutor"

        log.info(f"Tutor message {state.turn_count}: {reply}...")
        state.messages.append(reply)
        state.consecutive_irrelevant_count = 0
        return state

    @node(XRaySessionState)
    def tutor_response(self, state: XRaySessionState) -> XRaySessionState:
        log.info("Starting xray tutor response...")
        medical_llm = create_llm(Config.MEDICAL_MODEL)
        system_prompt = create_response_tutor_system_prompt(state)
        user_prompt = create_response_tutor_response_user_prompt(state)

        system_prompt, sources = augment_with_rag(system_prompt, build_xray_query(state))

        reply = medical_llm.invoke([system_prompt, user_prompt])
        clean_model_response(reply)
        attach_sources(reply, sources)
        message = build_output_message(reply.content)
        message.name = "tutor"

        log.info(f"Tutor message {state.turn_count}: {reply}...")
        state.messages.append(reply)
        return state

    @node(XRaySessionState)
    def tutor_wrong_impression(self, state: XRaySessionState) -> XRaySessionState:
        log.info("Starting xray tutor wrong impression...")
        medical_llm = create_llm(Config.MEDICAL_MODEL)
        system_prompt = create_wrong_impression_tutor_system_prompt(state)
        user_prompt = create_wrong_impression_tutor_user_prompt(state)

        system_prompt, sources = augment_with_rag(system_prompt, build_xray_query(state))

        reply = medical_llm.invoke([system_prompt, user_prompt])
        clean_model_response(reply)
        attach_sources(reply, sources)
        message = build_output_message(reply.content)
        message.name = "tutor"

        log.info(f"Tutor message {state.turn_count}: {reply}...")
        state.messages.append(reply)
        return state
