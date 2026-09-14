"""Dev-only script to generate a mermaid diagram of the compiled graph."""

import re

from langchain_core.runnables.graph_mermaid import draw_mermaid_png

from orchestrator.graph import graph

mermaid = graph.get_graph(xray=True).draw_mermaid()

# Sanitize syntax that the mermaid.ink API rejects:
# - HTML entities/tags in node labels
# - Dots inside dotted-edge labels (e.g. SessionType.ANAMNESIS) break the parser
mermaid = mermaid.replace("&nbsp;", " ").replace("<p>", "").replace("</p>", "")
mermaid = re.sub(r"-\.\s+(.+?)\s+\.->", lambda m: f"-.->|{m.group(1).strip()}|", mermaid)

png_data = draw_mermaid_png(mermaid)

with open("graph_diagram.png", "wb") as f:
    f.write(png_data)

print("Diagram saved to graph_diagram.png")
