import logging

from domains.xray.state import XRaySessionState
from domains.xray.prompts.presenter import create_presenter_system_prompt, create_presenter_user_prompt
from llm.models import clean_model_response, create_llm 
from llm.config import Config
from utils.messages import build_output_message
from utils.helpers import node

log = logging.getLogger(__name__)

@node(XRaySessionState)
def presenter(state: XRaySessionState) -> XRaySessionState:
    system_prompt = create_presenter_system_prompt(state)
    user_prompt = create_presenter_user_prompt()

    medical_llm = create_llm(Config.CHAT_MODEL)
    reply = medical_llm.invoke([system_prompt, user_prompt])
    clean_model_response(reply)
    message = build_output_message(reply.content)
    reply.name = "presentation"
    
    log.info(f"Presenter xray message {state.turn_count}: {reply}...")
    state.messages.append(message)

    return state
