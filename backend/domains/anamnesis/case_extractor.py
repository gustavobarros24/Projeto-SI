import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import BadRequestError
from pydantic import BaseModel, Field, ValidationError

from llm.config import Config
from llm.models import clean_model_response, create_llm
from rag.config import RAGConfig
from rag.extractors import extract_text


log = logging.getLogger(__name__)


class ExtractedCaseFields(BaseModel):
    """Structured clinical fields extracted from a real case document.

    Title and description are intentionally NOT here — they are filled by the
    teacher so that the student-facing case label never leaks the diagnosis.
    """

    patient_name: str = Field(description="Patient's name as written in the record.")
    patient_age: int = Field(description="Patient's age in years.")
    patient_gender: str = Field(description="Patient's gender (e.g. male, female).")
    hidden_diagnosis: str = Field(
        description="The final or working diagnosis the student must reach."
    )
    symptoms: list[str] = Field(
        description="List of clinically relevant symptoms reported in the case."
    )
    patient_emotional_state: str = Field(
        description="One short word describing the patient's emotional state "
        "(e.g. anxious, calm, distressed, cooperative)."
    )


_SYSTEM_PROMPT = (
    "You are a medical record analyst. Read the clinical case below and return "
    "ONE valid JSON object — no markdown fences, no prose before or after.\n"
    "The JSON object MUST have exactly these keys:\n"
    "  - patient_name (string)\n"
    "  - patient_age (integer, years; 0 if unknown)\n"
    '  - patient_gender (string; "male" | "female" | "" if unknown)\n'
    "  - hidden_diagnosis (string; final/working diagnosis as stated)\n"
    "  - symptoms (array of short strings; one per clinically relevant symptom, "
    "no investigations, no treatment)\n"
    '  - patient_emotional_state (single short word, e.g. "anxious", "calm", '
    '"neutral" by default)\n'
    "Use empty string or 0 if a field is genuinely missing — never invent."
)


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_case_fields(file_bytes: bytes, mime: str) -> ExtractedCaseFields:
    text = extract_text(file_bytes, mime).strip()
    if not text:
        raise ValueError("Document produced no extractable text")

    cap = RAGConfig.EXTRACT_MAX_CHARS
    if len(text) <= cap:
        return _extract_one(text)

    splitter = RecursiveCharacterTextSplitter(chunk_size=cap, chunk_overlap=200)
    chunks = [c for c in splitter.split_text(text) if c.strip()]
    log.info("[case_extractor] document split into %d chunks", len(chunks))

    parts: list[ExtractedCaseFields] = []
    for i, chunk in enumerate(chunks, 1):
        part = _extract_one(chunk)
        log.info(
            "[case_extractor] chunk %d/%d → %d symptoms, diagnosis=%r",
            i,
            len(chunks),
            len(part.symptoms),
            (part.hidden_diagnosis or "")[:60],
        )
        parts.append(part)

    return _merge(parts)


def _extract_one(text: str) -> ExtractedCaseFields:
    # bind(max_tokens=512) shrinks the server-reserved output budget so the
    # full prompt + reservation fit in n_ctx=4096 with margin. JSON for the
    # six short fields is comfortably under that.
    llm = create_llm(Config.MEDICAL_MODEL).bind(max_tokens=512)
    try:
        reply = llm.invoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=text),
            ]
        )
    except BadRequestError as e:
        msg = str(e)
        if "n_keep" in msg or "context length" in msg:
            raise ValueError(
                "Document too long for the configured model context (n_ctx). "
                "Reduce the file size or restart the MedGemma server with a "
                "larger --ctx-size."
            ) from e
        raise

    clean_model_response(reply)
    match = _JSON_BLOCK_RE.search(reply.content)
    if not match:
        raise ValueError(f"LLM returned no JSON object. Raw response: {reply.content[:200]!r}")

    try:
        return ExtractedCaseFields.model_validate_json(match.group(0))
    except ValidationError as e:
        raise ValueError(f"LLM returned malformed JSON: {e}") from e


def _merge(parts: list[ExtractedCaseFields]) -> ExtractedCaseFields:
    def first_non_empty(values: list[str]) -> str:
        for v in values:
            if v:
                return v
        return ""

    def first_positive(values: list[int]) -> int:
        for v in values:
            if v and v > 0:
                return v
        return 0

    def longest(values: list[str]) -> str:
        best = ""
        for v in values:
            if v and len(v) > len(best):
                best = v
        return best

    seen: set[str] = set()
    symptoms: list[str] = []
    for p in parts:
        for s in p.symptoms:
            key = s.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            symptoms.append(s.strip())

    return ExtractedCaseFields(
        patient_name=first_non_empty([p.patient_name for p in parts]),
        patient_age=first_positive([p.patient_age for p in parts]),
        patient_gender=first_non_empty([p.patient_gender for p in parts]),
        hidden_diagnosis=longest([p.hidden_diagnosis for p in parts]),
        symptoms=symptoms,
        patient_emotional_state=first_non_empty(
            [p.patient_emotional_state for p in parts]
        ),
    )
