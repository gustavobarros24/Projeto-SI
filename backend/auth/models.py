import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="student", server_default="student")

    # per-module progression (levels 1-5, gained by accumulating session-score XP)
    anamnesis_level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    anamnesis_xp: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    radiology_level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    radiology_xp: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    chats: Mapped[list["Chat"]] = relationship(back_populates="user")


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    thread_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="chats")
