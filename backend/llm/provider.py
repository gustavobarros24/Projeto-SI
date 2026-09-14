import os
import re
from enum import Enum

from langchain_core.messages import AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama


class Provider(str, Enum):
    MEDGEMMA = "medgemma"
    OLLAMA = "ollama"


_PROVIDER = Provider(os.getenv("LLM_PROVIDER", Provider.MEDGEMMA))

_models: dict[Provider, BaseChatModel] = {
    # Provider.MEDGEMMA: ChatOpenAI(
    #     model=os.getenv("MEDGEMMA_MODEL", "google/medgemma-1.5-4b-it"),
    #     api_key=os.getenv("LLM_API_KEY", "dummy-value"),
    #     base_url=os.getenv("LLM_BASE_URL", "http://localhost:8000/v1"),
    #     temperature=0.1,
    #     max_tokens=2048,
    # ),
    Provider.MEDGEMMA: ChatOpenAI(
        model=os.getenv("MEDGEMMA_MODEL", "unsloth/medgemma-27b-it-GGUF:Q8_0"),
        api_key=os.getenv("LLM_API_KEY", "dummy-value"),
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:8080/v1"),
        temperature=0.1,
        max_tokens=2048,
    ),
    Provider.OLLAMA: ChatOllama(model="llama3.1"),
}


def get_chat_model() -> BaseChatModel:
    return _models[_PROVIDER]


def clean_model_response(reply: AIMessage) -> AIMessage:
    """Remove o conteúdo entre os tokens <unused94> e <unused95> do conteúdo da resposta."""
    cleaned_content = re.sub(
        r"<unused94>.*?<unused95>", "", reply.content, flags=re.DOTALL
    )
    cleaned_content = cleaned_content.strip()

    reply.content = cleaned_content

    return reply
