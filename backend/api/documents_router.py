import asyncio
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse

from auth.models import User
from auth.utils import get_current_user, require_teacher
from rag.extractors import SUPPORTED_MIMES
from rag.ingest import delete_document, get_document, ingest_document, list_documents


log = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB

_EXT_TO_MIME = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".md": "text/markdown",
}


def _resolve_mime(upload: UploadFile) -> str:
    mime = (upload.content_type or "").lower()
    if mime in SUPPORTED_MIMES:
        return mime
    ext = Path(upload.filename or "").suffix.lower()
    return _EXT_TO_MIME.get(ext, mime)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_teacher),
):
    mime = _resolve_mime(file)
    if mime not in SUPPORTED_MIMES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {MAX_UPLOAD_BYTES // (1024*1024)} MB",
        )

    try:
        doc = await asyncio.to_thread(
            ingest_document, data, file.filename or "document", mime, current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.exception("Document ingestion failed")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "mime_type": doc.mime_type,
        "created_at": doc.created_at,
    }


@router.get("")
async def list_all_documents(current_user: User = Depends(get_current_user)):
    docs = await asyncio.to_thread(list_documents)
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "mime_type": d.mime_type,
            "uploaded_by": str(d.uploaded_by),
            "created_at": d.created_at,
        }
        for d in docs
    ]


@router.get("/{document_id}")
async def get_document_file(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    doc = await asyncio.to_thread(get_document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    path = Path(doc.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=410, detail="Document file no longer available")
    return FileResponse(
        path=path,
        media_type=doc.mime_type,
        filename=doc.filename,
        content_disposition_type="inline",
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(
    document_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
):
    deleted = await asyncio.to_thread(delete_document, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
