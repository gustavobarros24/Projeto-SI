from langchain_core.messages import SystemMessage, HumanMessage

from orchestrator.state import OrchestratorState
from utils.messages import get_last_human_message

def create_module_router_system_prompt() -> SystemMessage:
    return SystemMessage(
        content="""# ROLE ASSIGNMENT (PERSONA)
You are a routing assistant for a medical study application.

# TASK
Identify which module the student wants to use based on the previous messages in the session.

# PROVIDED INPUT DATA
Available modules:
- radiology: practice radiology image analysis (X-ray).
- anamnesis: practice clinical history-taking with a virtual patient.

# REQUIRED OUTPUT FORMAT
- Respond with the most appropriate module for the student."""
)

def create_module_router_user_prompt(state: OrchestratorState) -> HumanMessage:
    last_message = get_last_human_message(state.messages)
    content = f"""
<last_message>
{last_message}
</last_message>
"""
    return HumanMessage(content=content)
