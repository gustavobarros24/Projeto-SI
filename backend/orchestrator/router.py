import logging
from pydantic import BaseModel, Field

from orchestrator.prompts.router import create_module_router_system_prompt, create_module_router_user_prompt
from orchestrator.state import OrchestratorState, SessionType
from utils.helpers import node
from llm.models import create_llm
from llm.config import Config

log = logging.getLogger(__name__)


class RouteToModuleOutput(BaseModel):
    module: SessionType = Field(
        ..., description="Recommended study module for the student."
    )


@node(OrchestratorState)
def router(state: OrchestratorState) -> OrchestratorState:
    # When the student already made an explicit selection in the UI, trust that
    # over the LLM classifier — avoids the rare case where the model misreads
    # the welcome message and routes to the wrong module.
    if state.anamnesis_case_id:
        log.info("Orchestrator router: forced ANAMNESIS (anamnesis_case_id present)")
        state.module = SessionType.ANAMNESIS
        return state
    if state.radiology_case_id:
        log.info("Orchestrator router: forced RADIOLOGY (radiology_case_id present)")
        state.module = SessionType.RADIOLOGY
        return state

    log.info("Running orchestrator router...")
    system_prompt = create_module_router_system_prompt()
    user_prompt = create_module_router_user_prompt(state)

    chat_model = create_llm(Config.CHAT_MODEL)
    classifier_llm = chat_model.with_structured_output(RouteToModuleOutput)
    response = classifier_llm.invoke([system_prompt, user_prompt])

    log.info(f"AI classifier {Config.CHAT_MODEL.name}: {response}...")
    state.module = response.module

    return state
