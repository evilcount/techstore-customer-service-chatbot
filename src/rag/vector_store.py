from __future__ import annotations

from pathlib import Path
from typing import Protocol

import chromadb
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


DEFAULT_PERSIST_DIRECTORY = Path("chroma_db/techstore_knowledge")
DEFAULT_COLLECTION_NAME = "techstore_knowledge"


class Embeddings(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


class TechStoreVectorStore:
    def __init__(
        self,
        *,
        persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embeddings: Embeddings | None = None,
    ) -> None:
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.embeddings = embeddings or OpenAIEmbeddings(model="text-embedding-3-small")
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self.persist_directory))
        self._collection = self._client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents: list[Document]) -> None:
        if not documents:
            return

        texts = [document.page_content for document in documents]
        ids = [_document_id(document, index) for index, document in enumerate(documents)]
        self._collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=[document.metadata for document in documents],
            embeddings=self.embeddings.embed_documents(texts),
        )

    def similarity_search(self, query: str, *, k: int = 4) -> list[Document]:
        result = self._collection.query(
            query_embeddings=[self.embeddings.embed_query(query)],
            n_results=k,
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        return [
            Document(page_content=content, metadata=metadata or {})
            for content, metadata in zip(documents, metadatas)
        ]


def create_or_load_vector_store(
    *,
    persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embeddings: Embeddings | None = None,
) -> TechStoreVectorStore:
    return TechStoreVectorStore(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embeddings=embeddings,
    )


def _document_id(document: Document, index: int) -> str:
    source = str(document.metadata.get("source", "unknown"))
    chunk_index = document.metadata.get("chunk_index", index)
    return f"{source}:{chunk_index}"
