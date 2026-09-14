from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import RAGConfig


def split_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAGConfig.CHUNK_SIZE,
        chunk_overlap=RAGConfig.CHUNK_OVERLAP,
    )
    return [c for c in splitter.split_text(text) if c.strip()]
