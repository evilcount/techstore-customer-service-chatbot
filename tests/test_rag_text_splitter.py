from langchain_core.documents import Document

from src.rag.text_splitter import split_documents


def test_split_documents_preserves_metadata():
    source = Document(
        page_content="Warranty coverage applies. " * 80,
        metadata={"source": "warranty.md", "title": "Warranty", "document_type": "md"},
    )

    chunks = split_documents([source], chunk_size=120, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(chunk.metadata["source"] == "warranty.md" for chunk in chunks)
    assert all(chunk.metadata["title"] == "Warranty" for chunk in chunks)
    assert all(chunk.metadata["chunk_index"] == index for index, chunk in enumerate(chunks))


def test_split_documents_keeps_short_document_as_single_chunk():
    source = Document(
        page_content="Returns are allowed for 30 days.",
        metadata={"source": "returns.md", "title": "Returns", "document_type": "md"},
    )

    chunks = split_documents([source], chunk_size=500, chunk_overlap=80)

    assert len(chunks) == 1
    assert chunks[0].page_content == "Returns are allowed for 30 days."
    assert chunks[0].metadata["chunk_index"] == 0
