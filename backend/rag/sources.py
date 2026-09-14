from rag.retriever import RetrievedChunk


def dedupe_sources(chunks: list[RetrievedChunk]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for c in chunks:
        if c.document_id in seen:
            continue
        seen.add(c.document_id)
        out.append(
            {
                "id": c.document_id,
                "title": c.filename,
                "url": f"/documents/{c.document_id}",
            }
        )
    return out
