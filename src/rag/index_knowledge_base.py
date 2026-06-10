from __future__ import annotations

from pathlib import Path

from src.rag.document_loader import load_documents
from src.rag.text_splitter import split_documents
from src.rag.vector_store import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_PERSIST_DIRECTORY,
    TechStoreVectorStore,
    create_or_load_vector_store,
)


DEFAULT_KNOWLEDGE_BASE = Path("docs/knowledge_base")


def index_knowledge_base(
    *,
    knowledge_base_path: str | Path = DEFAULT_KNOWLEDGE_BASE,
    persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> tuple[TechStoreVectorStore, int]:
    documents = load_documents(knowledge_base_path)
    chunks = split_documents(documents)
    vector_store = create_or_load_vector_store(
        persist_directory=persist_directory,
        collection_name=collection_name,
    )
    vector_store.add_documents(chunks)
    return vector_store, len(chunks)
