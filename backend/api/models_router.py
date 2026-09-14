from fastapi import APIRouter

from llm.config import Config
from llm.models import create_provider

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/health")
async def check_models_health():
    try:
        available = _get_available_models()

        errors_list = []
        if Config.MEDICAL_MODEL.name not in available:
            errors_list.append(f"Medical model {Config.MEDICAL_MODEL.name} not available")
        if Config.CHAT_MODEL.name not in available:
            errors_list.append(f"Chat model {Config.CHAT_MODEL.name} not available")
        if len(errors_list) > 0:
            return {"status": "error", "message": ". ".join(errors_list)}

        return {"status": "ok", "message": "All models are healthy."}
    except Exception as e:
        print(f"Medical LLM health check failed: {e}")
        return {"status": "error", "message": "Failed to check model health."}


def _get_available_models():
    chat_model_provider = create_provider(Config.CHAT_MODEL)
    medical_model_provider = create_provider(Config.MEDICAL_MODEL)
    available = []

    try:
        chat_models_list = chat_model_provider.models.list()
        available_chat_models = [m.id for m in chat_models_list.data]
        available.extend(available_chat_models)
    except Exception as e:
        print(f"Failed to fetch chat models: {e}")
    
    try:
        medical_models_list = medical_model_provider.models.list()
        available_medical_models = [m.id for m in medical_models_list.data]
        available.extend(available_medical_models)
    except Exception as e:
        print(f"Failed to fetch medical models: {e}")

    return available
