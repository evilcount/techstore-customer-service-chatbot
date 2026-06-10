from pathlib import Path

import pytest

from src.rag.document_loader import load_document, load_documents


def test_load_markdown_document_includes_source_metadata(tmp_path):
    path = tmp_path / "policy.md"
    path.write_text("# Returns\n\nReturns are allowed for 30 days.", encoding="utf-8")

    docs = load_document(path)

    assert len(docs) == 1
    assert "Returns are allowed" in docs[0].page_content
    assert docs[0].metadata["source"] == str(path)
    assert docs[0].metadata["title"] == "policy.md"
    assert docs[0].metadata["document_type"] == "md"


def test_load_text_document_includes_source_metadata(tmp_path):
    path = tmp_path / "external.txt"
    path.write_text("External text reference.", encoding="utf-8")

    docs = load_document(path)

    assert len(docs) == 1
    assert docs[0].page_content == "External text reference."
    assert docs[0].metadata["source"] == str(path)
    assert docs[0].metadata["title"] == "external.txt"
    assert docs[0].metadata["document_type"] == "txt"


def test_load_documents_reads_directory_files(tmp_path):
    (tmp_path / "a.md").write_text("Alpha policy", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Beta policy", encoding="utf-8")

    docs = load_documents(tmp_path)

    assert [doc.metadata["title"] for doc in docs] == ["a.md", "b.txt"]
    assert [doc.page_content for doc in docs] == ["Alpha policy", "Beta policy"]


def test_load_document_rejects_unknown_extension(tmp_path):
    path = tmp_path / "image.png"
    path.write_text("not supported", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported document type"):
        load_document(path)
