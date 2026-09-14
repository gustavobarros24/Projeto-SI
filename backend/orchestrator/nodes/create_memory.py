import logging

from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore

from orchestrator.state import OrchestratorState
from orchestrator.prompts.create_memory import create_memory_system_prompt, create_memory_user_prompt
from orchestrator.constants import NAMESPACE_PREFIX, MEMORY_KEY
from schemas.memory import LongTermMemoryOutput
from llm.models import create_llm
from llm.config import Config

log = logging.getLogger(__name__)

def create_memory(state: OrchestratorState, config: RunnableConfig, store: BaseStore):
    student_id = state.student_id
    if not student_id:
        raise ValueError("Student ID is required in the state to load the student profile.")

    namespace = (NAMESPACE_PREFIX, student_id)
    existing_memories = store.get(namespace, MEMORY_KEY)

    formatted_memory = []
    if existing_memories and existing_memories.value:
        formatted_memory = existing_memories.value.get("weak_areas", [])

    system_prompt = create_memory_system_prompt(state)
    user_prompt = create_memory_user_prompt(state, formatted_memory)

    llm = create_llm(Config.CHAT_MODEL)
    updated_memory = llm.with_structured_output(LongTermMemoryOutput).invoke([system_prompt, user_prompt])
    log.info(f"Updating memory for student {student_id} with weak areas: {updated_memory}")

    store.put(namespace, MEMORY_KEY, {"weak_areas": updated_memory.weak_areas})
