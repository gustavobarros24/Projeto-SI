import logging

from domains.anamnesis.state import AnamnesisSessionState
from domains.anamnesis.prompts.patient import create_patient_system_prompt, create_patient_user_prompt
from utils.helpers import node
from llm.models import create_llm, clean_model_response
from llm.config import Config
from utils.messages import build_output_message

log = logging.getLogger(__name__)

@node(AnamnesisSessionState)
def patient(state: AnamnesisSessionState) -> AnamnesisSessionState:
    log.info("Starting patient anamnesis...")
    system_prompt = create_patient_system_prompt(state)
    user_prompt = create_patient_user_prompt(state)

    chat_llm = create_llm(Config.CHAT_MODEL)
    reply = chat_llm.invoke([system_prompt, user_prompt])
    clean_model_response(reply)
    message = build_output_message(reply.content)
    message.name = "patient"

    log.info(f"Patient message {state.turn_count}: {reply}...")
    state.messages.append(reply)
    return state
