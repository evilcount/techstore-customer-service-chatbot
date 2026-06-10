from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document


SUPPORTED_TEXT_EXTENSIONS = {".md", ".txt"}


def load_document(path: str | Path) -> list[Document]:
    """Load one local document with metadata suitable for RAG retrieval."""
    document_path = Path(path)
    if not document_path.exists():
        raise FileNotFoundError(f"Document not found: {document_path}")

    extension = document_path.suffix.lower()
    if extension in SUPPORTED_TEXT_EXTENSIONS:
        return [_load_text_document(document_path)]
    if extension == ".pdf":
        return _load_pdf_document(document_path)

    raise ValueError(f"Unsupported document type: {extension}")


def load_documents(path: str | Path) -> list[Document]:
    """Load one file or all supported files in a directory."""
    root = Path(path)
    if root.is_file():
        return load_document(root)

    documents: list[Document] = []
    for document_path in sorted(root.iterdir()):
        if document_path.is_file() and document_path.suffix.lower() in {
            ".md",
            ".txt",
            ".pdf",
        }:
            documents.extend(load_document(document_path))
    return documents


def _load_text_document(path: Path) -> Document:
    return Document(
        page_content=path.read_text(encoding="utf-8").strip(),
        metadata={
            "source": str(path),
            "title": path.name,
            "document_type": path.suffix.lower().lstrip("."),
        },
    )


def _load_pdf_document(path: Path) -> list[Document]:
    try:
        from langchain_community.document_loaders import PyPDFLoader
    except ImportError as exc:
        raise ImportError(
            "PDF loading requires langchain-community and pypdf. "
            "Install project requirements before loading PDFs."
        ) from exc

    loaded_pages = PyPDFLoader(str(path)).load()
    for page in loaded_pages:
        page.metadata.update(
            {
                "source": str(path),
                "title": path.name,
                "document_type": "pdf",
            }
        )
        if "page" in page.metadata:
            page.metadata["page_number"] = page.metadata["page"] + 1
    return loaded_pages
