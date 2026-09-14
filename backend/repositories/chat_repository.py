from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from auth.models import Chat


class ChatRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def create_chat(self, user_id: UUID) -> Chat:
        chat = Chat(user_id=user_id)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_by_thread_id(self, thread_id: str, user_id: UUID) -> Chat | None:
        result = await self.db.execute(
            select(Chat).where(Chat.thread_id == thread_id, Chat.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, chat: Chat) -> None:
        await self.db.delete(chat)
        await self.db.commit()

    async def update_name(self, chat: Chat, name: str) -> Chat:
        chat.name = name
        await self.db.commit()
        await self.db.refresh(chat)
        return chat
