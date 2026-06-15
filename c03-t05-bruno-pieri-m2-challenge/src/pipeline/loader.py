"""
pipeline/loader.py — Document loading and chunking for the TechStore Plus corpus.

Position in the architecture:
    data/  →  loader.py  →  vectorstore.py  →  retriever  →  LLM

Stop 1 (W4): Implement load_documents() and chunk_documents().

Design decisions you should document in your docstrings:
- Why RecursiveCharacterTextSplitter? It respects paragraph and sentence
  boundaries (trying '\\n\\n', '\\n', ' ' in order), which keeps semantically
  coherent chunks. A fixed-size splitter ignores structure entirely.
- Why add metadata (source, category, chunk_index)? The retriever returns
  Document objects; metadata lets the writer cite sources and lets the
  guardrail verifier trace claims back to specific files.
- Why chunk_size=500 as the default? See docs/chunk-experiment.md — you will
  empirically validate this in Stop 2.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------------------
# Constants — change these values to experiment; do not use magic numbers
# ---------------------------------------------------------------------------
CHUNK_SIZE: int = 500
"""Default chunk size in characters for RecursiveCharacterTextSplitter."""

CHUNK_OVERLAP: int = 50
"""Default overlap between adjacent chunks.

A 10% overlap (50 chars on a 500-char chunk) reduces the risk of splitting
a critical sentence across two chunks while keeping index size reasonable.
"""

DATA_DIR: Path = Path("data")
"""Default path to the TechStore Plus corpus directory, relative to project root."""

# Category labels derived from filename prefixes
_CATEGORY_MAP: dict[str, str] = {
    "product_manual": "product_manual",
    "support": "support_article",
    "policy": "policy",
}


def _infer_category(filename: str) -> str:
    """Infer the document category from the filename prefix.

    Supported prefixes: 'product_manual_*', 'support_*', 'policy_*'.
    Falls back to 'general' for unrecognised filenames.

    Args:
        filename: The bare filename (e.g. 'policy_return_policy.txt').

    Returns:
        One of 'product_manual', 'support_article', 'policy', or 'general'.
    """
    for prefix, category in _CATEGORY_MAP.items():
        if filename.startswith(prefix):
            return category
    return "general"


def load_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    """Load all .txt and .pdf files from *data_dir* and attach metadata.

    Only the top-level directory is loaded here; CSV tables are handled by
    ``src.multimodal.table_retriever.TableRetriever`` (Stop 3).

    Each returned Document has the following metadata keys:
    - ``source``:      filename (e.g. 'policy_return_policy.txt')
    - ``category``:   one of 'product_manual', 'support_article', 'policy', 'general'
    - ``file_path``:  full path as string

    After loading, print a summary:
    - Number of documents loaded
    - Total word count (approximate)

    Uses RecursiveCharacterTextSplitter-friendly loaders:
    - TextLoader with utf-8 encoding for .txt files preserves paragraph
      structure, which the splitter later uses as primary split boundaries.
    - PyPDFLoader for .pdf files when present in the corpus.

    Args:
        data_dir: Path to the corpus directory.  Defaults to :data:`DATA_DIR`.

    Returns:
        A list of :class:`~langchain_core.documents.Document` objects, one per file.

    Raises:
        FileNotFoundError: If *data_dir* does not exist.
        RuntimeError: If no supported files are found in *data_dir*.
    """
    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Data directory not found: {data_dir}. "
            "Make sure you are running from the project root."
        )

    documents: list[Document] = []

    txt_files = sorted(data_dir.glob("*.txt"))
    pdf_files = sorted(data_dir.glob("*.pdf"))

    if not txt_files and not pdf_files:
        raise RuntimeError(f"No supported (.txt / .pdf) files found in {data_dir}")

    for path in txt_files:
        loader = TextLoader(str(path), encoding="utf-8")
        docs = loader.load()
        filename = path.name
        for doc in docs:
            doc.metadata["source"] = filename
            doc.metadata["category"] = _infer_category(filename)
            doc.metadata["file_path"] = str(path)
        documents.extend(docs)

    for path in pdf_files:
        loader = PyPDFLoader(str(path))
        docs = loader.load()
        filename = path.name
        for doc in docs:
            doc.metadata["source"] = filename
            doc.metadata["category"] = _infer_category(filename)
            doc.metadata["file_path"] = str(path)
        documents.extend(docs)

    total_words = sum(len(doc.page_content.split()) for doc in documents)
    print(f"Loaded {len(documents)} documents | ~{total_words:,} words total")
    return documents


def chunk_documents(
    docs: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Split *docs* into overlapping chunks and add ``chunk_index`` metadata.

    Uses :class:`~langchain_text_splitters.RecursiveCharacterTextSplitter`,
    which splits on paragraph breaks ('\\n\\n') first, then line breaks ('\\n'),
    then spaces, then characters — preserving semantic boundaries as long as
    possible.  This is preferable to a fixed-size splitter because TechStore
    policy documents have clearly delimited sections that should stay together.

    Each returned chunk inherits the parent document's metadata and gains:
    - ``chunk_index``: integer position of this chunk within its source document
      (0-indexed).

    After chunking, print a summary:
    - Total chunk count
    - Average chunk length in characters

    Args:
        docs:           Documents to split (output of :func:`load_documents`).
        chunk_size:     Maximum characters per chunk.  Defaults to :data:`CHUNK_SIZE`.
        chunk_overlap:  Character overlap between consecutive chunks.
                        Defaults to :data:`CHUNK_OVERLAP`.

    Returns:
        A flat list of chunk :class:`~langchain_core.documents.Document` objects.

    Example::

        chunks = chunk_documents(docs)
        print(f"{len(chunks)} chunks, avg {sum(len(c.page_content) for c in chunks) // len(chunks)} chars")
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_documents(docs)

    # Assign chunk_index per source file
    source_counter: dict[str, int] = defaultdict(int)
    for chunk in raw_chunks:
        source = chunk.metadata.get("source", "unknown")
        chunk.metadata["chunk_index"] = source_counter[source]
        source_counter[source] += 1

    if raw_chunks:
        avg_len = sum(len(c.page_content) for c in raw_chunks) // len(raw_chunks)
    else:
        avg_len = 0
    print(f"Generated {len(raw_chunks)} chunks | avg {avg_len} chars/chunk")
    return raw_chunks
