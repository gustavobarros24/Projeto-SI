"""High-level helpers for applying RAG inside graph nodes.

Each clinical node follows the same shape: build a query from state, retrieve
top-K chunks above the threshold, inject them into the system prompt, and
attach the deduplicated source documents to the model's reply.
"""
import logging

from langchain_core.messages import AIMessage, SystemMessage

from rag.prompt import inject_context
from rag.retriever import retrieve
from rag.sources import dedupe_sources


log = logging.getLogger(__name__)


def augment_with_rag(system_prompt: SystemMessage, query: str) -> tuple[SystemMessage, list[dict]]:
    """Retrieve chunks for `query` and inject them into `system_prompt`.

    Returns the (possibly enriched) system prompt and the deduped source
    documents to attach to the reply. If retrieval returns nothing (no corpus,
    failure, or top-1 score below threshold) the prompt is returned unchanged
    and sources is an empty list.
    """
    chunks = retrieve(query)
    if not chunks:
        log.info("[RAG] no chunks injected (empty or below threshold)")
        return system_prompt, []
    sources = dedupe_sources(chunks)
    log.info(
        f"[RAG] injecting {len(chunks)} chunks → {len(sources)} source doc(s): "
        + ", ".join(s["title"] for s in sources)
    )
    return inject_context(system_prompt, chunks), sources


def attach_sources(reply: AIMessage, sources: list[dict]) -> AIMessage:
    """Attach source documents to an AIMessage's additional_kwargs."""
    if not sources:
        return reply
    existing = dict(reply.additional_kwargs or {})
    existing["source_documents"] = sources
    reply.additional_kwargs = existing
    return reply
