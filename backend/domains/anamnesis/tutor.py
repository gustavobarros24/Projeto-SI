import logging

from core.tutor import ITutor
from llm.provider import clean_model_response
from llm.models import create_llm
from llm.config import Config
from domains.anamnesis.state import AnamnesisSessionState
from domains.anamnesis.prompts.tutor.tutor_off_track import create_off_track_tutor_system_prompt, create_off_track_tutor_user_prompt
from domains.anamnesis.prompts.tutor.tutor_wrong_diagnosis import create_wrong_diagnosis_tutor_system_prompt, create_wrong_diagnosis_tutor_user_prompt
from rag.integration import attach_sources, augment_with_rag
from rag.query import build_anamnesis_query
from utils.helpers import node
from llm.models import create_llm, clean_model_response
from llm.config import Config
from utils.messages import build_output_message

log = logging.getLogger(__name__)


class AnamnesisTutor(ITutor[AnamnesisSessionState]):
    @node(AnamnesisSessionState)
    def tutor_off_track(self, state: AnamnesisSessionState) -> AnamnesisSessionState:
        log.info("Starting anamnesis tutor off track...")
        medical_llm = create_llm(Config.MEDICAL_MODEL)
        system_prompt = create_off_track_tutor_system_prompt(state)
        user_prompt = create_off_track_tutor_user_prompt(state)

        system_prompt, sources = augment_with_rag(system_prompt, build_anamnesis_query(state))

        reply = medical_llm.invoke([system_prompt, user_prompt])
        clean_model_response(reply)
        attach_sources(reply, sources)
        message = build_output_message(reply.content)
        message.name = "tutor"

        log.info(f"Tutor message {state.turn_count}: {reply}...")
        state.messages.append(reply)
        state.consecutive_irrelevant_count = 0
        return state

    @node(AnamnesisSessionState)
    def tutor_wrong_diagnosis(self, state: AnamnesisSessionState) -> AnamnesisSessionState:
        log.info("Starting anamnesis tutor wrong diagnosis...")
        medical_llm = create_llm(Config.MEDICAL_MODEL)
        system_prompt = create_wrong_diagnosis_tutor_system_prompt(state)
        user_prompt = create_wrong_diagnosis_tutor_user_prompt(state)

        system_prompt, sources = augment_with_rag(system_prompt, build_anamnesis_query(state))

        reply = medical_llm.invoke([system_prompt, user_prompt])
        clean_model_response(reply)
        attach_sources(reply, sources)
        message = build_output_message(reply.content)
        message.name = "tutor"

        log.info(f"Tutor message {state.turn_count}: {reply}...")
        state.messages.append(reply)
        return state
