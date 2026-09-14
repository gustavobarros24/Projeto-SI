import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from rag.config import RAGConfig
from rag.db import SyncSession

from domains.anamnesis.case_extractor import ExtractedCaseFields, extract_case_fields
from domains.anamnesis.case_model import AnamnesisCase


log = logging.getLogger(__name__)


_EXT_BY_MIME = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}


def _store_file(file_bytes: bytes, mime: str) -> tuple[uuid.UUID, Path]:
    RAGConfig.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = _EXT_BY_MIME.get(mime, "bin")
    case_id = uuid.uuid4()
    storage_path = Path(RAGConfig.UPLOAD_DIR) / f"{case_id}.{ext}"
    storage_path.write_bytes(file_bytes)
    return case_id, storage_path


def create_case_from_upload(
    file_bytes: bytes,
    filename: str,
    mime: str,
    uploaded_by: uuid.UUID,
) -> AnamnesisCase:
    extracted = extract_case_fields(file_bytes, mime)
    case_id, storage_path = _store_file(file_bytes, mime)

    with SyncSession() as session:
        case = AnamnesisCase(
            id=case_id,
            title="",
            description="",
            patient_name=extracted.patient_name,
            patient_age=extracted.patient_age,
            patient_gender=extracted.patient_gender,
            hidden_diagnosis=extracted.hidden_diagnosis,
            symptoms=list(extracted.symptoms),
            patient_emotional_state=extracted.patient_emotional_state,
            status="draft",
            original_filename=filename,
            storage_path=str(storage_path),
            mime_type=mime,
            uploaded_by=uploaded_by,
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        log.info(
            "[anamnesis_case] created draft %s from upload (%s, %d symptoms)",
            case.id,
            filename,
            len(case.symptoms),
        )
        return case


def re_extract_case(case_id: uuid.UUID) -> ExtractedCaseFields | None:
    with SyncSession() as session:
        case = session.get(AnamnesisCase, case_id)
        if case is None:
            return None
        path = Path(case.storage_path)
        if not path.is_file():
            raise FileNotFoundError(f"Original file missing: {path}")
        file_bytes = path.read_bytes()
        mime = case.mime_type
    return extract_case_fields(file_bytes, mime)


def list_cases(only_published: bool) -> list[AnamnesisCase]:
    with SyncSession() as session:
        query = session.query(AnamnesisCase)
        if only_published:
            query = query.filter(AnamnesisCase.status == "published")
        return list(query.order_by(AnamnesisCase.created_at.desc()).all())


def get_case(case_id: uuid.UUID) -> AnamnesisCase | None:
    with SyncSession() as session:
        return session.get(AnamnesisCase, case_id)


_EDITABLE_FIELDS = {
    "title",
    "description",
    "level",
    "patient_name",
    "patient_age",
    "patient_gender",
    "hidden_diagnosis",
    "symptoms",
    "patient_emotional_state",
    "status",
}


def update_case(case_id: uuid.UUID, fields: dict) -> AnamnesisCase | None:
    with SyncSession() as session:
        case = session.get(AnamnesisCase, case_id)
        if case is None:
            return None
        for key, value in fields.items():
            if key in _EDITABLE_FIELDS and value is not None:
                setattr(case, key, value)
        case.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(case)
        return case


def delete_case(case_id: uuid.UUID) -> bool:
    with SyncSession() as session:
        case = session.get(AnamnesisCase, case_id)
        if case is None:
            return False
        storage = Path(case.storage_path)
        session.delete(case)
        session.commit()
        if storage.is_file():
            try:
                storage.unlink()
            except OSError as e:
                log.warning("Could not remove file %s: %s", storage, e)
    return True
