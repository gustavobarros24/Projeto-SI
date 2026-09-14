"""Speech-to-text via the Gemma 4 native-audio model.

The model is served over an OpenAI-compatible endpoint (LM Studio / llama.cpp).
Gemma 4 transcribes audio through the chat-completions API using an
`input_audio` content part — it returns plain text, never audio. This module is
the single place to adjust if the serving stack expects a different request
shape (e.g. a future `/v1/audio/transcriptions` endpoint).
"""

import base64
import logging

from llm.config import Config
from llm.models import create_provider

log = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = create_provider(Config.STT_MODEL)
    return _client


# Audio container/codec hint passed to the model alongside the base64 payload.
_FORMAT_BY_MIME = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/wave": "wav",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "mp4",
}

_LANGUAGE_LABEL = {
    "en": "English",
    "pt": "European Portuguese",
}


def _prompt(language: str) -> str:
    label = _LANGUAGE_LABEL.get((language or "").lower(), "the spoken language")
    return (
        f"Transcribe the following audio to text in {label}. "
        "Output ONLY the verbatim transcription — no preface, quotes, or commentary."
    )


def transcribe(audio_bytes: bytes, mime: str, language: str = "en") -> str:
    """Transcribe an audio clip to text. Returns the transcript (may be empty)."""
    client = _get_client()
    audio_format = _FORMAT_BY_MIME.get((mime or "").lower(), "wav")
    encoded = base64.b64encode(audio_bytes).decode("ascii")

    response = client.chat.completions.create(
        model=Config.STT_MODEL.name,
        temperature=0.0,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _prompt(language)},
                    {
                        "type": "input_audio",
                        "input_audio": {"data": encoded, "format": audio_format},
                    },
                ],
            }
        ],
    )

    transcript = (response.choices[0].message.content or "").strip()
    log.info(
        "[transcription] %d bytes (%s) → %r", len(audio_bytes), mime, transcript[:80]
    )
    return transcript
