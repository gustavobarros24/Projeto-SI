import logging
from dataclasses import dataclass

from sqlalchemy import text

from rag.config import RAGConfig
from rag.db import SyncSession
from rag.embeddings import embed_query


log = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    filename: str
    text: str
    score: float


_RETRIEVAL_SQL = text(
    """
    SELECT c.id::text AS chunk_id,
           c.document_id::text AS document_id,
           d.filename AS filename,
           c.text AS text,
           1 - (c.embedding <=> CAST(:qvec AS vector)) AS score
    FROM document_chunks c
    JOIN documents d ON d.id = c.document_id
    ORDER BY c.embedding <=> CAST(:qvec AS vector)
    LIMIT :k
    """
)


def retrieve(
    query: str,
    *,
    threshold: float | None = None,
    k: int | None = None,
) -> list[RetrievedChunk]:
    if not query or not query.strip():
        return []

    threshold = RAGConfig.SIMILARITY_THRESHOLD if threshold is None else threshold
    k = RAGConfig.TOP_K if k is None else k

    try:
        qvec = embed_query(query)
    except Exception as e:
        log.warning(f"RAG embedding failed, skipping retrieval: {e}")
        return []

    vec_literal = "[" + ",".join(f"{v:.8f}" for v in qvec) + "]"

    try:
        with SyncSession() as session:
            rows = session.execute(
                _RETRIEVAL_SQL, {"qvec": vec_literal, "k": k}
            ).all()
    except Exception as e:
        log.warning(f"RAG retrieval query failed, returning no chunks: {e}")
        return []

    if not rows:
        log.info(f"[RAG] retrieval empty for query={query!r}")
        return []

    log.info(f"[RAG] retrieval for query={query!r} (threshold={threshold:.3f})")
    for i, r in enumerate(rows, 1):
        marker = "KEEP" if float(r.score) >= threshold else "DROP"
        log.info(
            f"[RAG]   #{i} {marker}  score={float(r.score):.3f}  doc={r.filename}  text={r.text[:120]!r}"
        )

    top_score = float(rows[0].score)
    if top_score < threshold:
        log.info(
            f"[RAG] top-1 score {top_score:.3f} below threshold {threshold:.3f}; discarding all chunks."
        )
        return []

    return [
        RetrievedChunk(
            chunk_id=r.chunk_id,
            document_id=r.document_id,
            filename=r.filename,
            text=r.text,
            score=float(r.score),
        )
        for r in rows
    ]
