from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    BaseMessage,
)
from utils.helpers import generate_uuid

class MessageType(str, Enum):
    HUMAN  = "human"
    SYSTEM = "system"
    AI = "ai"

class Message(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    content: str
    type: MessageType
    name: Optional[str] = None
    # Mirror of `AIMessage.additional_kwargs` so RAG metadata (e.g.
    # source_documents) survives `state.model_dump()` when langchain AIMessages
    # are appended to `state.messages` (typed `list[Message]`). Pydantic's
    # duck-typed serialization walks Message's schema, so the field must exist
    # here for the attribute to be picked up off the AIMessage.
    additional_kwargs: dict[str, Any] = Field(default_factory=dict)

    @staticmethod
    def toBaseMessages(message: "Message") -> BaseMessage:
        content = message.content 

        if not content:
            raise ValueError(f"No content message.")
        if message.type == MessageType.HUMAN:
            return HumanMessage(content=content)
        elif message.type == MessageType.AI:
            return AIMessage(content=content)
        elif message.type == MessageType.SYSTEM:
            return SystemMessage(content=content)
        else:
            raise ValueError(f"Unknown message type: {message.type}.")

def build_input_message(content: str, type: MessageType = MessageType.HUMAN) -> Message:
    message = Message(id=generate_uuid(), content=content, type=type)
    return message

def build_output_message(content: str, type: MessageType = MessageType.AI) -> Message:
    message = Message(id=generate_uuid(), content=content, type=type)
    return message

def get_last_human_message(messages: list[Message]) -> Message:
    last_message = next(
        (m for m in reversed(messages) if m.type == MessageType.HUMAN)
    )
    if not last_message:
        raise Exception("No human message found.")
    return last_message

def get_last_n_human_messages(messages: list[Message], n: int) -> list[Message]:
    human_messages = [
        m for m in messages if m.type == MessageType.HUMAN
    ]
    if not human_messages:
        raise Exception("No human messages found.")
    return human_messages[-n:]
