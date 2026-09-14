from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader


PDF_MIMES = {"application/pdf"}
DOCX_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
TEXT_MIMES = {"text/plain", "text/markdown"}

SUPPORTED_MIMES = PDF_MIMES | DOCX_MIMES | TEXT_MIMES


def extract_text(data: bytes, mime: str) -> str:
    if mime in PDF_MIMES:
        reader = PdfReader(BytesIO(data))
        return "\n\n".join((p.extract_text() or "") for p in reader.pages)
    if mime in DOCX_MIMES:
        doc = DocxDocument(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if mime in TEXT_MIMES:
        return data.decode("utf-8", errors="replace")
    raise ValueError(f"Unsupported mime type: {mime}")
