import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class VoiceNote(Base):
    """A student's recorded utterance, transcribed and fed into the chat graph.

    The audio is kept on disk (uploads/) so the student message can be replayed
    later (WhatsApp-style); the row links it to the chat thread and its owner.
    """

    __tablename__ = "voice_notes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # the chat thread this utterance belongs to (Chat.thread_id, a unique string)
    thread_id: Mapped[str] = mapped_column(String(255), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    # the recorded audio kept on disk for playback
    original_filename: Mapped[str] = mapped_column(String(512))
    storage_path: Mapped[str] = mapped_column(String(1024))
    mime_type: Mapped[str] = mapped_column(String(255))

    # transcription produced at capture time (debugging / future search)
    transcript: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
