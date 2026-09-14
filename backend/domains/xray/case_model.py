import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class RadiologyCase(Base):
    __tablename__ = "radiology_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # student-facing label (no findings spoilers)
    title: Mapped[str] = mapped_column(String(255), default="")

    # difficulty level (1-5), set only by the teacher; gates student selection by level
    level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    # publication state: "draft" (only teacher sees) | "published" (students can pick)
    status: Mapped[str] = mapped_column(String(16), default="draft", index=True)

    # ground-truth extracted from the image by MedGemma at upload time
    ground_findings: Mapped[list[str]] = mapped_column(JSONB, default=list)
    impression: Mapped[str] = mapped_column(Text, default="")

    # original uploaded image kept on disk for re-extraction / display
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
