from copy import deepcopy
from enum import Enum

from typing import Iterable, Final

from langchain_core.messages import HumanMessage, SystemMessage

from llm.config import GEMMA
from llm.models import create_llm
from utils.helpers import ModelT
from utils.logger import get_logger


log = get_logger("llm", console=False)

_BASE_TRANSLATOR_PROMPT: Final[str] = """
 You are a professional medical translator.
 Translate the user message into {language}.

- Preserve clinical terminology, numbers, units and formatting.
- Output ONLY the translation. Do not add prefaces, explanations, quotes or notes. 
- If the input is already in the target language, return it unchanged.
"""

class Language(str, Enum):
    EN = "en"
    PT = "pt"

_TARGET_LANGUAGE: Final[dict[Language, str]] = {
    Language.EN: "English (United Kingdom)",
    Language.PT: "Portuguese (Portugal)",
}

def get_language(language: Language) -> str:
    return _TARGET_LANGUAGE[language]

def _translator_llm():
    cfg = deepcopy(GEMMA)
    cfg.temperature = 0.0
    return create_llm(cfg)


def _system_prompt(language: Language) -> SystemMessage:
    return SystemMessage(
        content=_BASE_TRANSLATOR_PROMPT.format(language=get_language(language))
    )

def translate_model(model_instance: ModelT, language: Language, *, llm=None) -> ModelT:
    if llm is None:
        llm = _translator_llm()

    structured_llm = llm.with_structured_output(model_instance.__class__)
    new_prompt = _BASE_TRANSLATOR_PROMPT + "CRITICAL: Never translate, rename, or modify JSON field/key names. "
    response = structured_llm.invoke([
        SystemMessage(
            content=new_prompt.format(language=get_language(language))
        ),
        HumanMessage(content=model_instance.model_dump_json())
    ])
    return response

def translate(text: str, language: Language) -> str:
    if not text or not text.strip():
        return text

    llm = _translator_llm()
    prompt = _system_prompt(language)
    reply = llm.invoke([prompt, ("human", text)])
    translated = reply.content.strip()

    log.debug(
        "translate[%s] %r -> %r",
        language.value,
        text[:80],
        translated[:80],
    )
    return translated

