import logging

from openai import BadRequestError
from pydantic import BaseModel, Field

from llm.config import Config
from llm.models import create_llm
from utils.image import image_bytes_to_data_uri
from domains.xray.prompts.interpreter import (
    create_interpreter_system_prompt,
    create_interpreter_user_prompt,
)


log = logging.getLogger(__name__)


class ExtractedRadiologyFields(BaseModel):
    """Ground-truth fields extracted from a radiological image.

    The title and level are intentionally NOT here — they are set by the
    teacher; the student-facing label never leaks the findings.
    """

    ground_findings: list[str] = Field(
        description="Discrete radiological findings visible in the image."
    )
    impression: str = Field(
        description="Concise overall radiological impression."
    )


class _VisionOutput(BaseModel):
    impression: str = Field(
        ...,
        description="A concise definitive radiological impression summarizing the overall interpretation of the image.",
    )
    findings: list[str] = Field(
        ..., description="List of radiological findings identified in the image."
    )


def extract_findings_from_image(file_bytes: bytes, mime: str) -> ExtractedRadiologyFields:
    data_uri = image_bytes_to_data_uri(file_bytes, mime)

    system_prompt = create_interpreter_system_prompt()
    user_prompt = create_interpreter_user_prompt(data_uri)

    llm = create_llm(Config.MEDICAL_MODEL).with_structured_output(_VisionOutput)
    try:
        result: _VisionOutput = llm.invoke([system_prompt, user_prompt])
    except BadRequestError as e:
        msg = str(e)
        if "n_keep" in msg or "context length" in msg:
            raise ValueError(
                "Image too large for the configured model context (n_ctx). "
                "Reduce the image resolution or restart the MedGemma server with "
                "a larger --ctx-size."
            ) from e
        raise

    log.info(
        "[radiology_case_extractor] %d findings, impression=%r",
        len(result.findings),
        (result.impression or "")[:60],
    )
    return ExtractedRadiologyFields(
        ground_findings=result.findings,
        impression=result.impression,
    )
