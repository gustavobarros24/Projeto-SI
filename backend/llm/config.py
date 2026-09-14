import os
from enum import Enum

class ModelProvider(str, Enum):
    OPENAI = "openai"


class ModelConfig:
    name: str # ID do modelo
    temperature: float # Controla a aleatoriedade das respostas (0.0 a 1.0)
    provider: ModelProvider # API do modelo
    max_tokens: int

    def __init__(
            self,
            name: str,
            temperature: float,
            provider: ModelProvider, 
            base_url: str,
            api_key: str,
            max_tokens: int = 2048,
        ):
        self.name = name
        self.temperature = temperature
        self.provider = provider
        self.base_url = base_url
        self.api_key = api_key
        self.max_tokens = max_tokens


MEDGEMMA = ModelConfig(
    name=os.getenv("MEDICAL_MODEL", "unsloth/medgemma-27b-it-GGUF:Q8_0"),
    temperature=0.1,
    provider=ModelProvider.OPENAI,
    base_url=os.getenv("MEDICAL_LLM_BASE_URL", "http://localhost:8080/v1"),
    api_key=os.getenv("MEDICAL_LLM_API_KEY", "dummy-value"),
    max_tokens=2048
)
GEMMA = ModelConfig(
    name=os.getenv("CHAT_MODEL", "gemma"),
    temperature=0.7,
    provider=ModelProvider.OPENAI,
    base_url=os.getenv("CHAT_LLM_BASE_URL", "http://localhost:8081/v1"),
    api_key=os.getenv("CHAT_LLM_API_KEY", "dummy-value"),
    max_tokens=2048
)
# Speech-to-text (Gemma 4 native audio) served over an OpenAI-compatible
# endpoint. Defaults to the chat model/endpoint since Gemma 4 E2B is already
# audio-capable; override when the audio model is served separately.
STT = ModelConfig(
    name=os.getenv("STT_MODEL", os.getenv("CHAT_MODEL", "gemma")),
    temperature=0.0,
    provider=ModelProvider.OPENAI,
    base_url=os.getenv("STT_LLM_BASE_URL", os.getenv("CHAT_LLM_BASE_URL", "http://localhost:8081/v1")),
    api_key=os.getenv("STT_LLM_API_KEY", "dummy-value"),
    max_tokens=2048
)


class Config:
    CHAT_MODEL = GEMMA
    MEDICAL_MODEL = MEDGEMMA
    STT_MODEL = STT

    # Absolute base URL the frontend uses to fetch backend-served files (e.g. a
    # radiology case image). Used to build image_url for stored radiology cases.
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8008")
