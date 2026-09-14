import logging
import uuid
from pathlib import Path

from rag.chunker import split_text
from rag.config import RAGConfig
from rag.db import SyncSession
from rag.embeddings import embed_documents
from rag.extractors import extract_text
from rag.models import Document, DocumentChunk


log = logging.getLogger(__name__)


_EXT_BY_MIME = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}


def ingest_document(file_bytes: bytes, filename: str, mime: str, uploaded_by: uuid.UUID) -> Document:
    text_body = extract_text(file_bytes, mime)
    chunks = split_text(text_body)
    if not chunks:
        raise ValueError("Document produced no text chunks after extraction.")

    RAGConfig.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = _EXT_BY_MIME.get(mime, "bin")
    doc_id = uuid.uuid4()
    storage_path = Path(RAGConfig.UPLOAD_DIR) / f"{doc_id}.{ext}"
    storage_path.write_bytes(file_bytes)

    embeddings = embed_documents(chunks)

    with SyncSession() as session:
        doc = Document(
            id=doc_id,
            filename=filename,
            storage_path=str(storage_path),
            mime_type=mime,
            uploaded_by=uploaded_by,
        )
        session.add(doc)
        session.flush()

        for i, (chunk_text, vec) in enumerate(zip(chunks, embeddings)):
            session.add(
                DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    text=chunk_text,
                    embedding=vec,
                )
            )
        session.commit()
        session.refresh(doc)
        log.info(
            f"Ingested document {doc.id} ({filename}) with {len(chunks)} chunks."
        )
        return doc


def delete_document(document_id: uuid.UUID) -> bool:
    with SyncSession() as session:
        doc = session.get(Document, document_id)
        if not doc:
            return False
        storage = Path(doc.storage_path)
        session.delete(doc)
        session.commit()
        if storage.is_file():
            try:
                storage.unlink()
            except OSError as e:
                log.warning(f"Could not remove file {storage}: {e}")
    return True


def list_documents() -> list[Document]:
    with SyncSession() as session:
        return list(session.query(Document).order_by(Document.created_at.desc()).all())


def get_document(document_id: uuid.UUID) -> Document | None:
    with SyncSession() as session:
        return session.get(Document, document_id)
