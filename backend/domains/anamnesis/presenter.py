import logging

from domains.anamnesis.state import AnamnesisSessionState
from domains.anamnesis.prompts.presenter import create_presenter_system_prompt, create_presenter_user_prompt
from utils.helpers import node
from llm.models import create_llm, clean_model_response
from llm.config import Config
from utils.messages import build_output_message

log = logging.getLogger(__name__)


@node(AnamnesisSessionState)
def presenter(state: AnamnesisSessionState) -> AnamnesisSessionState:
    log.info("Starting anamnesis presenter...")
    system_prompt = create_presenter_system_prompt(state)
    user_prompt = create_presenter_user_prompt()

    chat_model = create_llm(Config.CHAT_MODEL)
    reply = chat_model.invoke([system_prompt, user_prompt])
    clean_model_response(reply)
    message = build_output_message(reply.content)
    message.name = "presentation"

    log.info(f"Presenter anamnesis message {state.turn_count}: {reply}...")
    state.messages.append(message)

    return state
