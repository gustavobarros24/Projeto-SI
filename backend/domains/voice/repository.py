import logging
import uuid
from pathlib import Path

from rag.config import RAGConfig
from rag.db import SyncSession

from domains.voice.model import VoiceNote


log = logging.getLogger(__name__)


_EXT_BY_MIME = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/wave": "wav",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "m4a",
}


def _store_audio_file(file_bytes: bytes, mime: str) -> tuple[uuid.UUID, Path]:
    RAGConfig.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = _EXT_BY_MIME.get(mime, "bin")
    note_id = uuid.uuid4()
    storage_path = Path(RAGConfig.UPLOAD_DIR) / f"{note_id}.{ext}"
    storage_path.write_bytes(file_bytes)
    return note_id, storage_path


def create_voice_note(
    file_bytes: bytes,
    filename: str,
    mime: str,
    user_id: uuid.UUID,
    thread_id: str,
    transcript: str,
) -> VoiceNote:
    note_id, storage_path = _store_audio_file(file_bytes, mime)

    with SyncSession() as session:
        note = VoiceNote(
            id=note_id,
            thread_id=thread_id,
            user_id=user_id,
            original_filename=filename,
            storage_path=str(storage_path),
            mime_type=mime,
            transcript=transcript,
        )
        session.add(note)
        session.commit()
        session.refresh(note)
        log.info(
            "[voice_note] stored %s for thread %s (%d bytes)",
            note.id,
            thread_id,
            len(file_bytes),
        )
        return note


def get_voice_note(note_id: uuid.UUID) -> VoiceNote | None:
    with SyncSession() as session:
        return session.get(VoiceNote, note_id)
