from langchain_core.documents import Document

from src.rag.vector_store import create_or_load_vector_store


class FakeEmbeddings:
    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        normalized = text.lower()
        return [float("return" in normalized), float("warranty" in normalized)]


def test_vector_store_persists_and_reloads_documents(tmp_path):
    persist_dir = tmp_path / "chroma"
    documents = [
        Document(
            page_content="Customers can return laptops within 30 calendar days.",
            metadata={"source": "returns.md", "title": "Returns", "chunk_index": 0},
        ),
        Document(
            page_content="Warranty covers defects for one year.",
            metadata={"source": "warranty.md", "title": "Warranty", "chunk_index": 1},
        ),
    ]

    store = create_or_load_vector_store(
        persist_directory=persist_dir,
        collection_name="test_collection",
        embeddings=FakeEmbeddings(),
    )
    store.add_documents(documents)

    reloaded = create_or_load_vector_store(
        persist_directory=persist_dir,
        collection_name="test_collection",
        embeddings=FakeEmbeddings(),
    )
    results = reloaded.similarity_search("return laptop", k=1)

    assert len(results) == 1
    assert "return laptops" in results[0].page_content
    assert results[0].metadata["source"] == "returns.md"
