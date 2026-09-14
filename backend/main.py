from dotenv import load_dotenv
load_dotenv()


import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db import Base, engine, get_db
from orchestrator.graph import graph
from auth.routes import router as auth_router
from auth.utils import get_current_user
from auth.models import User, Chat
from api.chat_router import router as chat_router
from api.models_router import router as models_router
from api.documents_router import router as documents_router
from api.anamnesis_cases_router import router as anamnesis_cases_router
from api.radiology_cases_router import router as radiology_cases_router
from api.voice_router import router as voice_router
import rag.models  # noqa: F401 — ensure tables registered before create_all
import domains.anamnesis.case_model  # noqa: F401 — ensure anamnesis_cases table registered
import domains.xray.case_model  # noqa: F401 — ensure radiology_cases table registered
import domains.voice.model  # noqa: F401 — ensure voice_notes table registered
from services.state_serializer import serialize_state
from utils.messages import build_input_message 
from llm.translator import Language
import warnings

warnings.filterwarnings("error", category=UserWarning)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(models_router)
app.include_router(documents_router)
app.include_router(anamnesis_cases_router)
app.include_router(radiology_cases_router)
app.include_router(voice_router)


class ChatRequest(BaseModel):
    thread_id: str
    message: str
    is_diagnosis: bool = False
    language: Language = Language.EN


class DiagnoseRequest(BaseModel):
    diagnosis: str


@app.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student_id = str(current_user.id)
    config = {"configurable": {"thread_id": req.thread_id}}

    current_state = graph.get_state(config)
    is_new_thread = current_state.values == {}

    if is_new_thread:
        user_input = build_input_message(req.message)
        response = graph.invoke(
            {"student_id": student_id, "messages": [user_input], "language": req.language},
            config=config,
        )

        # check if the thread_id already exists in the database to avoid duplicates
        result = await db.execute(select(Chat).where(Chat.thread_id == req.thread_id))
        existing_chat = result.scalar_one_or_none()
        if not existing_chat:
            # save the new chat on database
            chat = Chat(thread_id=req.thread_id, user_id=current_user.id)
            db.add(chat)
            await db.commit()
            await db.refresh(chat)
    else:
        resume_value = {"content": req.message, "is_diagnosis": req.is_diagnosis} if req.is_diagnosis else req.message
        response = graph.invoke(
            Command(resume=resume_value),
            config=config,
        )

    # When the subgraph is interrupted (e.g. await_input), the parent's
    # invoke response doesn't include the subgraph's internal state.
    # Use get_state(subgraphs=True) to read the subgraph's state instead.
    state_snapshot = graph.get_state(config, subgraphs=True)
    module = state_snapshot.values.get("module")

    if state_snapshot.tasks:
        subgraph_values = state_snapshot.tasks[0].state.values
        return serialize_state(subgraph_values, module=module)

    return serialize_state(response, module=module)


# This endpoint is used by the frontend to load the chat history when opening an existing thread.
@app.get("/chat/{thread_id}")
async def chat(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student_id = str(current_user.id)
    config = {"configurable": {"thread_id": thread_id}}

    # search thread_id in the database to verify if it exists and belongs to the current user
    result = await db.execute(
        select(Chat).where(
            Chat.thread_id == thread_id and Chat.user_id == current_user.id
        )
    )
    chat = result.scalar()

    if not chat:
        raise HTTPException(status_code=404, detail="Thread not found")

    current_state = graph.get_state(config)
    is_new_thread = current_state.values == {}

    if is_new_thread:
        return {"messages": [], "session": None}

    state_snapshot = graph.get_state(config, subgraphs=True)
    module = state_snapshot.values.get("module")

    if state_snapshot.tasks:
        subgraph_values = state_snapshot.tasks[0].state.values
        return serialize_state(subgraph_values, module=module)

    return serialize_state(current_state.values, module=module)


@app.post("/chat/{thread_id}/give-up")
async def give_up(
    thread_id: str,
    current_user: User = Depends(get_current_user),
):
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke(
        Command(resume={"type": "give_up"}),
        config=config,
    )

    state_snapshot = graph.get_state(config, subgraphs=True)

    if state_snapshot.tasks:
        subgraph_values = state_snapshot.tasks[0].state.values
        return serialize_state(subgraph_values)

    values = state_snapshot.values
    if not values.get("session_summary") or not values.get("final_report"):
        for history_state in graph.get_state_history(config):
            if history_state.tasks:
                task_state = history_state.tasks[0].state
                if task_state and (task_state.values.get("session_summary") or task_state.values.get("final_report")):
                    return serialize_state(task_state.values)

    return serialize_state(values)


@app.post("/chat/{thread_id}/diagnose")
async def diagnose(
    thread_id: str,
    req: DiagnoseRequest,
    current_user: User = Depends(get_current_user),
):
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke(
        Command(resume={"content": req.diagnosis, "is_diagnosis": True}),
        config=config,
    )

    state_snapshot = graph.get_state(config, subgraphs=True)

    if state_snapshot.tasks:
        subgraph_values = state_snapshot.tasks[0].state.values
        return serialize_state(subgraph_values)

    values = state_snapshot.values
    if not values.get("session_summary") or not values.get("final_report"):
        for history_state in graph.get_state_history(config):
            if history_state.tasks:
                task_state = history_state.tasks[0].state
                if task_state and (task_state.values.get("session_summary") or task_state.values.get("final_report")):
                    return serialize_state(task_state.values)

    return serialize_state(values)


# Fetch all chats for the current user
@app.get("/chats")
async def get_chats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chat)
        .where(Chat.user_id == current_user.id)
        .order_by(Chat.created_at.desc())
    )
    chats = result.scalars().all()

    return [
        {
            "thread_id": chat.thread_id,
            "created_at": chat.created_at,
            "name": chat.name,
        }
        for chat in chats
    ]
