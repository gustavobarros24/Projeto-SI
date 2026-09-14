from langchain_core.messages import SystemMessage

from rag.retriever import RetrievedChunk


_INSTRUCTION = (
    "Use the reference excerpts above to ground your reasoning when appropriate. "
    "Do NOT add inline citations, numeric references like '[1]', or phrases such as "
    "'according to document X' in your reply. Write naturally as if the knowledge "
    "were your own. The student will see the source documents separately as buttons."
)


def inject_context(system_prompt: SystemMessage, chunks: list[RetrievedChunk]) -> SystemMessage:
    if not chunks:
        return system_prompt

    parts = ["## Reference excerpts"]
    for i, c in enumerate(chunks, 1):
        parts.append(f"[excerpt {i} — {c.filename}]\n{c.text.strip()}")
    parts.append(_INSTRUCTION)

    addition = "\n\n".join(parts)
    return SystemMessage(content=f"{system_prompt.content}\n\n{addition}")
