import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from rag.config import RAGConfig
from rag.db import SyncSession

from domains.xray.case_extractor import (
    ExtractedRadiologyFields,
    extract_findings_from_image,
)
from domains.xray.case_model import RadiologyCase


log = logging.getLogger(__name__)


_EXT_BY_MIME = {
    "image/png": "png",
    "image/jpeg": "jpg",
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
) -> RadiologyCase:
    extracted = extract_findings_from_image(file_bytes, mime)
    case_id, storage_path = _store_file(file_bytes, mime)

    with SyncSession() as session:
        case = RadiologyCase(
            id=case_id,
            title="",
            level=1,
            status="draft",
            ground_findings=list(extracted.ground_findings),
            impression=extracted.impression,
            original_filename=filename,
            storage_path=str(storage_path),
            mime_type=mime,
            uploaded_by=uploaded_by,
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        log.info(
            "[radiology_case] created draft %s from upload (%s, %d findings)",
            case.id,
            filename,
            len(case.ground_findings),
        )
        return case


def re_extract_case(case_id: uuid.UUID) -> ExtractedRadiologyFields | None:
    with SyncSession() as session:
        case = session.get(RadiologyCase, case_id)
        if case is None:
            return None
        path = Path(case.storage_path)
        if not path.is_file():
            raise FileNotFoundError(f"Original file missing: {path}")
        file_bytes = path.read_bytes()
        mime = case.mime_type
    return extract_findings_from_image(file_bytes, mime)


def list_cases(only_published: bool) -> list[RadiologyCase]:
    with SyncSession() as session:
        query = session.query(RadiologyCase)
        if only_published:
            query = query.filter(RadiologyCase.status == "published")
        return list(query.order_by(RadiologyCase.created_at.desc()).all())


def get_case(case_id: uuid.UUID) -> RadiologyCase | None:
    with SyncSession() as session:
        return session.get(RadiologyCase, case_id)


_EDITABLE_FIELDS = {
    "title",
    "level",
    "ground_findings",
    "impression",
    "status",
}


def update_case(case_id: uuid.UUID, fields: dict) -> RadiologyCase | None:
    with SyncSession() as session:
        case = session.get(RadiologyCase, case_id)
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
        case = session.get(RadiologyCase, case_id)
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
