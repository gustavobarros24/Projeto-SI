from fastapi import APIRouter, Depends

from schemas.chat_schema import (
    DeleteChatResponse,
    NewChatRequest,
    NewChatResponse,
    UpdateChatRequest,
    UpdateChatResponse,
)
from services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/new", response_model=NewChatResponse)
async def create_chat(
    data: NewChatRequest,
    service: ChatService = Depends(),
):
    return await service.create_chat(
        data.message,
        data.language,
        data.anamnesis_case_id,
        data.radiology_case_id,
    )


@router.patch("/{thread_id}", response_model=UpdateChatResponse)
async def rename_chat(
    thread_id: str,
    data: UpdateChatRequest,
    service: ChatService = Depends(),
):
    return await service.rename_chat(thread_id, data.name)


@router.delete("/{thread_id}", response_model=DeleteChatResponse)
async def delete_chat(
    thread_id: str,
    service: ChatService = Depends(),
):
    return await service.delete_chat(thread_id)
