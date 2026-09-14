import asyncio
import uuid

from fastapi import Depends, HTTPException

from orchestrator.graph import graph
from llm.memory import checkpointer
from llm.translator import Language
from auth.utils import get_current_user
from auth.models import User
from domains.anamnesis.case_repository import get_case
from domains.xray.case_repository import get_case as get_radiology_case
from repositories.chat_repository import ChatRepository
from services.state_serializer import serialize_state
from utils.messages import build_input_message, MessageType


class ChatService:
    def __init__(
        self,
        repo: ChatRepository = Depends(),
        user: User = Depends(get_current_user),
    ):
        self.repo = repo
        self.user = user

    async def create_chat(
        self,
        message: str,
        language: Language = Language.EN,
        anamnesis_case_id: str | None = None,
        radiology_case_id: str | None = None,
    ) -> dict:
        case_title: str | None = None
        if anamnesis_case_id:
            try:
                case_uuid = uuid.UUID(anamnesis_case_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid anamnesis_case_id")
            case = await asyncio.to_thread(get_case, case_uuid)
            if case is None:
                raise HTTPException(status_code=404, detail="Anamnesis case not found")
            if case.status != "published":
                raise HTTPException(status_code=403, detail="Anamnesis case is not published")
            if case.level > self.user.anamnesis_level:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient level for this anamnesis case",
                )
            case_title = case.title or None

        if radiology_case_id:
            try:
                rad_uuid = uuid.UUID(radiology_case_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid radiology_case_id")
            rad_case = await asyncio.to_thread(get_radiology_case, rad_uuid)
            if rad_case is None:
                raise HTTPException(status_code=404, detail="Radiology case not found")
            if rad_case.status != "published":
                raise HTTPException(status_code=403, detail="Radiology case is not published")
            if rad_case.level > self.user.radiology_level:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient level for this radiology case",
                )
            case_title = rad_case.title or None

        new_chat = await self.repo.create_chat(self.user.id)
        if case_title:
            await self.repo.update_name(new_chat, case_title)

        config = {"configurable": {"thread_id": new_chat.thread_id}}
        student_id = str(self.user.id)
        user_input = build_input_message(message)

        graph_input: dict = {"student_id": student_id, "messages": [user_input], "language": language}
        if anamnesis_case_id:
            graph_input["anamnesis_case_id"] = anamnesis_case_id
        if radiology_case_id:
            graph_input["radiology_case_id"] = radiology_case_id

        graph.invoke(graph_input, config=config)

        state_snapshot = graph.get_state(config, subgraphs=True)
        if state_snapshot.tasks:
            state_values = state_snapshot.tasks[0].state.values
        else:
            state_values = graph.get_state(config).values

        serialized = serialize_state(state_values)
        return {"thread_id": new_chat.thread_id, **serialized}

    async def delete_chat(self, thread_id: str) -> dict:
        chat = await self.repo.get_by_thread_id(thread_id, self.user.id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat não encontrado")

        await self.repo.delete(chat)
        checkpointer.delete_thread(thread_id)

        return {"thread_id": thread_id, "detail": "Chat apagado"}

    async def rename_chat(self, thread_id: str, name: str) -> dict:
        chat = await self.repo.get_by_thread_id(thread_id, self.user.id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat não encontrado")

        updated = await self.repo.update_name(chat, name.strip())
        return {"thread_id": updated.thread_id, "name": updated.name}
