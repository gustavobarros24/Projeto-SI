from langgraph.graph import StateGraph, END

from domains.anamnesis.graph import build_anamnesis_graph
from domains.xray.graph import build_xray_graph
from orchestrator.state import OrchestratorState, SessionType
from orchestrator.router import router
from llm.memory import checkpointer, store
from utils.logger import get_logger
from orchestrator.nodes import award_xp, create_memory, load_student_profile


log = get_logger("llm", console=False)


log.info("Starting orchestrator...")
anamnesis_subgraph = build_anamnesis_graph()
xray_subgraph = build_xray_graph()

graph_builder = StateGraph(OrchestratorState)
graph_builder.add_node("load_student_profile", load_student_profile)
graph_builder.add_node("router", router)
graph_builder.add_node("radiology", xray_subgraph)
graph_builder.add_node("anamnesis", anamnesis_subgraph)
graph_builder.add_node("award_xp", award_xp)
graph_builder.add_node("create_memory", create_memory)

graph_builder.set_entry_point("load_student_profile")

graph_builder.add_edge("load_student_profile", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.module,
    {
        SessionType.RADIOLOGY: "radiology",
        SessionType.ANAMNESIS: "anamnesis",
    },
)

graph_builder.add_edge("radiology", "award_xp")
graph_builder.add_edge("anamnesis", "award_xp")
graph_builder.add_edge("award_xp", "create_memory")
graph_builder.add_edge("create_memory", END)

graph = graph_builder.compile(checkpointer=checkpointer, store=store)
