from openai import OpenAI

from rag.config import RAGConfig


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=RAGConfig.EMBED_API_KEY,
            base_url=RAGConfig.EMBED_BASE_URL,
        )
    return _client


def embed_query(text: str) -> list[float]:
    return embed_documents([text])[0]


def embed_documents(texts: list[str], batch_size: int = 16) -> list[list[float]]:
    out: list[list[float]] = []
    client = _get_client()
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=RAGConfig.EMBED_MODEL,
            input=batch,
        )
        out.extend(item.embedding for item in response.data)
    return out
