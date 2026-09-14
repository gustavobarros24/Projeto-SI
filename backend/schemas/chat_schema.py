from typing import Optional

from pydantic import BaseModel, Field

from llm.translator import Language


class NewChatRequest(BaseModel):
    message: str
    anamnesis_case_id: Optional[str] = None
    radiology_case_id: Optional[str] = None
    language: Language = Language.EN


class NewChatResponse(BaseModel):
    thread_id: str
    messages: list[dict]
    session: dict


class DeleteChatResponse(BaseModel):
    thread_id: str
    detail: str


class UpdateChatRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class UpdateChatResponse(BaseModel):
    thread_id: str
    name: str
