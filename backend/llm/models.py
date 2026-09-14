import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from openai import OpenAI

from llm.config import ModelConfig, ModelProvider

def create_llm(model_config: ModelConfig) -> BaseChatModel:
    if model_config.provider == ModelProvider.OPENAI:
        return ChatOpenAI(
            model=model_config.name,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            api_key=model_config.api_key,
            base_url=model_config.base_url,
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_config.provider}")

def create_provider(model_config: ModelConfig):
    """Cria um cliente para o modelo com base na configuração fornecida."""
    if model_config.provider == ModelProvider.OPENAI:
        return OpenAI(
            api_key=model_config.api_key,
            base_url=model_config.base_url,
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_config.provider}")

def clean_model_response(reply: AIMessage) -> AIMessage:
    """Remove o conteúdo entre os tokens <unused94> e <unused95> do conteúdo da resposta."""
    cleaned_content = re.sub(
        r"<unused94>.*?<unused95>", "", reply.content, flags=re.DOTALL
    )
    cleaned_content = cleaned_content.strip()

    reply.content = cleaned_content

    return reply
