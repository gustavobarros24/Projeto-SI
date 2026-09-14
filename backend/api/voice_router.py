import asyncio
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from langgraph.types import Command

from auth.models import User
from auth.utils import get_current_user
from orchestrator.graph import graph
from services.state_serializer import serialize_state
from services.transcription import transcribe
from domains.voice.repository import create_voice_note, get_voice_note


log = logging.getLogger(__name__)

router = APIRouter(tags=["voice"])

# Audio clips are short (≤30s for Gemma 4) — cap well below the document limit.
MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB

_AUDIO_MIMES = {
    "audio/webm",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
}
_EXT_TO_MIME = {
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
}


def _resolve_audio_mime(upload: UploadFile) -> str:
    # MediaRecorder sends e.g. "audio/webm;codecs=opus" — keep only the type.
    mime = (upload.content_type or "").lower().split(";")[0].strip()
    if mime in _AUDIO_MIMES:
        return mime
    ext = Path(upload.filename or "").suffix.lower()
    return _EXT_TO_MIME.get(ext, mime)


@router.post("/chat/voice")
async def chat_voice(
    file: UploadFile = File(...),
    thread_id: str = Form(...),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user),
):
    """Transcribe a recorded utterance and feed it into the chat graph as the
    next student turn. The audio is stored and linked to the resulting message
    (additional_kwargs["audio_id"]) so it can be replayed."""
    mime = _resolve_audio_mime(file)
    if mime not in _AUDIO_MIMES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio type: {file.content_type}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio")
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio exceeds maximum size of {MAX_AUDIO_BYTES // (1024 * 1024)} MB",
        )

    config = {"configurable": {"thread_id": thread_id}}

    # Voice input is only valid while the session is parked awaiting a turn.
    state_snapshot = graph.get_state(config, subgraphs=True)
    if not state_snapshot.tasks:
        raise HTTPException(status_code=409, detail="Session is not awaiting input")

    try:
        transcript = (await asyncio.to_thread(transcribe, data, mime, language)).strip()
    except Exception as e:
        log.exception("Transcription failed")
        raise HTTPException(status_code=502, detail=f"Transcription failed: {e}")

    if not transcript:
        raise HTTPException(status_code=422, detail="No speech detected")

    note = await asyncio.to_thread(
        create_voice_note,
        data,
        file.filename or "recording",
        mime,
        current_user.id,
        thread_id,
        transcript,
    )

    response = graph.invoke(
        Command(resume={"content": transcript, "audio_id": str(note.id)}),
        config=config,
    )

    state_snapshot = graph.get_state(config, subgraphs=True)
    module = state_snapshot.values.get("module")
    if state_snapshot.tasks:
        subgraph_values = state_snapshot.tasks[0].state.values
        return serialize_state(subgraph_values, module=module)
    return serialize_state(response, module=module)


@router.get("/voice-notes/{note_id}/file")
async def get_voice_note_file(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    note = await asyncio.to_thread(get_voice_note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Voice note not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your voice note")
    path = Path(note.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=410, detail="Audio file no longer available")
    return FileResponse(
        path=path,
        media_type=note.mime_type,
        filename=note.original_filename,
        content_disposition_type="inline",
    )
