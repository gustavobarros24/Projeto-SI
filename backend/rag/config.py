import os
from pathlib import Path


def _env_int(key: str, default: int) -> int:
    return int(os.getenv(key, str(default)))


def _env_float(key: str, default: float) -> float:
    return float(os.getenv(key, str(default)))


BACKEND_DIR = Path(__file__).resolve().parent.parent


class RAGConfig:
    EMBED_BASE_URL: str = os.getenv("RAG_EMBED_BASE_URL", "http://localhost:8082/v1")
    EMBED_MODEL: str = os.getenv("RAG_EMBED_MODEL", "bge-m3")
    EMBED_API_KEY: str = os.getenv("RAG_EMBED_API_KEY", "dummy-value")
    EMBED_DIM: int = _env_int("RAG_EMBED_DIM", 1024)

    SIMILARITY_THRESHOLD: float = _env_float("RAG_SIMILARITY_THRESHOLD", 0.55)
    TOP_K: int = _env_int("RAG_TOP_K", 3)

    CHUNK_SIZE: int = _env_int("RAG_CHUNK_SIZE", 800)
    CHUNK_OVERLAP: int = _env_int("RAG_CHUNK_OVERLAP", 100)

    # Per-call char cap for the anamnesis case extractor. Sized so that, with a
    # 512-token output budget and ~500 tokens of system + chat template, the
    # full prompt fits in n_ctx=4096 with a safety margin.
    EXTRACT_MAX_CHARS: int = _env_int("RAG_EXTRACT_MAX_CHARS", 10_000)

    UPLOAD_DIR: Path = Path(os.getenv("RAG_UPLOAD_DIR", str(BACKEND_DIR / "uploads")))
