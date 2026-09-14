import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class AnamnesisCase(Base):
    __tablename__ = "anamnesis_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # student-facing metadata (no diagnosis spoilers)
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(String(500), default="")

    # clinical fields used to seed AnamnesisSessionState
    patient_name: Mapped[str] = mapped_column(String(255))
    patient_age: Mapped[int] = mapped_column(Integer)
    patient_gender: Mapped[str] = mapped_column(String(32))
    hidden_diagnosis: Mapped[str] = mapped_column(Text)
    symptoms: Mapped[list[str]] = mapped_column(JSONB, default=list)
    patient_emotional_state: Mapped[str] = mapped_column(String(64))

    # difficulty level (1-5), set only by the teacher; gates student selection by level
    level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    # publication state: "draft" (only teacher sees) | "published" (students can pick)
    status: Mapped[str] = mapped_column(String(16), default="draft", index=True)

    # original uploaded file kept on disk for re-extraction / audit
    original_filename: Mapped[str] = mapped_column(String(512))
    storage_path: Mapped[str] = mapped_column(String(1024))
    mime_type: Mapped[str] = mapped_column(String(255))

    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
