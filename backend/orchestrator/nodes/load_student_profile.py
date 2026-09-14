from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore

from orchestrator.state import OrchestratorState, SessionType, StudentProfile
from orchestrator.constants import NAMESPACE_PREFIX, MEMORY_KEY
from utils.helpers import node
from utils.logger import get_logger

log = get_logger("llm", console=False)

@node(OrchestratorState)
def load_student_profile(state: OrchestratorState, config: RunnableConfig, store: BaseStore) -> OrchestratorState:
    student_id = state.student_id
    if not student_id:
        raise ValueError("Student ID is required in the state to load the student profile.")

    namespace = (NAMESPACE_PREFIX, student_id)
    existing_memory = store.get(namespace, MEMORY_KEY)

    weak_areas = []
    if existing_memory and existing_memory.value:
        weak_areas = existing_memory.value.get("weak_areas", [])

    log.info(f"Loaded weak_areas for student {student_id}: {weak_areas}")

    state.student_profile = StudentProfile(
        student_id=student_id,
        name="Test",
        radiology_level=1,
        anamnesis_level=1,
        radiology_sessions=0,
        anamnesis_sessions=0,
        weak_areas=weak_areas,
    )

    return state
