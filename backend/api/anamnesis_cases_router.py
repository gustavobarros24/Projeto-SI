import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from auth.models import User
from auth.utils import get_current_user, require_teacher
from domains.anamnesis.case_model import AnamnesisCase
from domains.anamnesis.case_repository import (
    create_case_from_upload,
    delete_case,
    get_case,
    list_cases,
    re_extract_case,
    update_case,
)
from rag.extractors import SUPPORTED_MIMES

from api.documents_router import MAX_UPLOAD_BYTES, _resolve_mime


log = logging.getLogger(__name__)

router = APIRouter(prefix="/anamnesis-cases", tags=["anamnesis-cases"])


_ALLOWED_STATUSES = {"draft", "published"}


class AnamnesisCaseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=500)
    level: Optional[int] = Field(default=None, ge=1, le=5)
    patient_name: Optional[str] = Field(default=None, max_length=255)
    patient_age: Optional[int] = Field(default=None, ge=0, le=150)
    patient_gender: Optional[str] = Field(default=None, max_length=32)
    hidden_diagnosis: Optional[str] = None
    symptoms: Optional[list[str]] = None
    patient_emotional_state: Optional[str] = Field(default=None, max_length=64)
    status: Optional[str] = None


def _to_student_summary(case: AnamnesisCase) -> dict:
    return {
        "id": str(case.id),
        "title": case.title,
        "description": case.description,
        "level": case.level,
    }


def _to_admin_summary(case: AnamnesisCase) -> dict:
    return {
        "id": str(case.id),
        "title": case.title,
        "description": case.description,
        "level": case.level,
        "status": case.status,
        "original_filename": case.original_filename,
        "uploaded_by": str(case.uploaded_by),
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


def _to_full(case: AnamnesisCase) -> dict:
    return {
        "id": str(case.id),
        "title": case.title,
        "description": case.description,
        "level": case.level,
        "patient_name": case.patient_name,
        "patient_age": case.patient_age,
        "patient_gender": case.patient_gender,
        "hidden_diagnosis": case.hidden_diagnosis,
        "symptoms": list(case.symptoms or []),
        "patient_emotional_state": case.patient_emotional_state,
        "status": case.status,
        "original_filename": case.original_filename,
        "mime_type": case.mime_type,
        "uploaded_by": str(case.uploaded_by),
        "created_at": case.created_at,
        "updated_at": case.updated_at,
    }


@router.get("")
async def list_published_cases(current_user: User = Depends(get_current_user)):
    cases = await asyncio.to_thread(list_cases, True)
    return [_to_student_summary(c) for c in cases]


@router.get("/admin")
async def list_all_cases(current_user: User = Depends(require_teacher)):
    cases = await asyncio.to_thread(list_cases, False)
    return [_to_admin_summary(c) for c in cases]


@router.get("/{case_id}")
async def get_case_full(
    case_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
):
    case = await asyncio.to_thread(get_case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return _to_full(case)


@router.get("/{case_id}/file")
async def get_case_file(
    case_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
):
    case = await asyncio.to_thread(get_case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    path = Path(case.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=410, detail="Case file no longer available")
    return FileResponse(
        path=path,
        media_type=case.mime_type,
        filename=case.original_filename,
        content_disposition_type="inline",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_case(
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
        case = await asyncio.to_thread(
            create_case_from_upload,
            data,
            file.filename or "case",
            mime,
            current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.exception("Anamnesis case upload failed")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    return _to_full(case)


@router.post("/{case_id}/re-extract")
async def re_extract(
    case_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
):
    try:
        extracted = await asyncio.to_thread(re_extract_case, case_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=410, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.exception("Re-extraction failed for case %s", case_id)
        raise HTTPException(status_code=500, detail=f"Re-extraction failed: {e}")

    if extracted is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return extracted.model_dump()


@router.patch("/{case_id}")
async def patch_case(
    case_id: uuid.UUID,
    payload: AnamnesisCaseUpdate,
    current_user: User = Depends(require_teacher),
):
    fields = payload.model_dump(exclude_unset=True)
    if "status" in fields and fields["status"] not in _ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status (must be one of {sorted(_ALLOWED_STATUSES)})",
        )

    case = await asyncio.to_thread(update_case, case_id, fields)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return _to_full(case)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_case(
    case_id: uuid.UUID,
    current_user: User = Depends(require_teacher),
):
    deleted = await asyncio.to_thread(delete_case, case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
    return None
