# Week 4 RAG TechStore Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Week 4 RAG pipeline to TechStore that indexes local knowledge-base documents, persists them in ChromaDB, answers grounded questions with source metadata, and lightly integrates with the existing chatbot.

**Architecture:** Build the RAG feature as additive modules under `src/rag/`, keeping Weeks 1-3 intact. Use local Markdown/TXT/PDF loading, LangChain text splitting, ChromaDB persistence, and a RAG assistant that can be injected into `MemoryAgent` without replacing the current LangGraph agent.

**Tech Stack:** Python, LangChain core/OpenAI/text splitters/community loaders, ChromaDB, pytest, Jupyter notebook, existing TechStore `src/` chatbot modules.

---

## File Structure

- Create `docs/knowledge_base/techstore_returns.md`: sample returns policy.
- Create `docs/knowledge_base/techstore_warranty.md`: sample warranty policy.
- Create `docs/knowledge_base/techstore_shipping.md`: sample shipping policy.
- Create `docs/knowledge_base/techstore_products.md`: sample product catalog snippets.
- Create `docs/knowledge_base/techstore_support.md`: sample support/escalation policy.
- Create `docs/knowledge_base/sample_external_document.txt`: external TXT example for the challenge.
- Modify `.gitignore`: ignore generated ChromaDB files under `chroma_db/`.
- Modify `requirements.txt`: add `chromadb`, `langchain-community`, `langchain-text-splitters`, and `pypdf`.
- Create `src/rag/__init__.py`: public exports for RAG modules.
- Create `src/rag/document_loader.py`: load `.md`, `.txt`, and `.pdf` files as LangChain `Document` objects with metadata.
- Create `src/rag/text_splitter.py`: split documents with metadata preserved.
- Create `src/rag/vector_store.py`: create/load ChromaDB collections and retrieve relevant chunks.
- Create `src/rag/rag_chain.py`: route knowledge questions, compose grounded prompts, and answer with sources.
- Modify `src/chains/memory_agent.py`: inject optional RAG assistant before the existing LangGraph agent.
- Create `tests/test_rag_document_loader.py`: loader coverage.
- Create `tests/test_rag_text_splitter.py`: splitter coverage.
- Create `tests/test_rag_chain.py`: retrieval and answer behavior with fakes.
- Create `tests/test_memory_agent_rag_unit.py`: chatbot integration coverage.
- Create `Week4_RAG_TechStore.ipynb`: notebook demonstration covering the Week 4 challenge deliverables.
- Modify `README.md`: document Week 4 purpose and running instructions.

---

### Task 1: Add TechStore Knowledge Base And Dependency Metadata

**Files:**
- Create: `docs/knowledge_base/techstore_returns.md`
- Create: `docs/knowledge_base/techstore_warranty.md`
- Create: `docs/knowledge_base/techstore_shipping.md`
- Create: `docs/knowledge_base/techstore_products.md`
- Create: `docs/knowledge_base/techstore_support.md`
- Create: `docs/knowledge_base/sample_external_document.txt`
- Modify: `.gitignore`
- Modify: `requirements.txt`

- [ ] **Step 1: Create the knowledge-base directory**

Run: `New-Item -ItemType Directory -Force docs\knowledge_base`

Expected: `docs\knowledge_base` exists.

- [ ] **Step 2: Add `techstore_returns.md`**

Create `docs/knowledge_base/techstore_returns.md` with:

```markdown
# TechStore Plus Returns Policy

TechStore Plus accepts returns for most products within 30 calendar days of delivery.
Laptops, tablets, smartphones, monitors, accessories, and unopened smart home devices
are eligible for standard returns when they are in good physical condition and include
the original charger, cables, manuals, and packaging.

Opened software, downloadable products, gift cards, and customized devices are final
sale unless required by law or covered by a verified product defect.

Customers should start a return from their order history or contact customer support
with the order number, product name, reason for return, and preferred resolution.
TechStore Plus can provide a refund, exchange, or store credit depending on inventory
and product condition.

If an item arrives damaged, customers must contact support within 7 calendar days of
delivery and provide photos of the item, packaging, shipping label, and order number.
Damaged delivery cases are routed to Priority Support.

Refunds are issued to the original payment method after warehouse inspection. Standard
refund processing takes 5 to 10 business days after the returned item is received.
```

- [ ] **Step 3: Add `techstore_warranty.md`**

Create `docs/knowledge_base/techstore_warranty.md` with:

```markdown
# TechStore Plus Warranty Policy

Most new laptops, tablets, smartphones, monitors, routers, and smart home devices sold
by TechStore Plus include a one-year limited manufacturer warranty. Warranty coverage
usually begins on the delivery date and covers defects in materials or workmanship.

The warranty does not cover accidental damage, liquid exposure, unauthorized repairs,
lost accessories, cosmetic wear, or damage caused by misuse. Customers who purchased
TechCare Plus may have additional accidental damage benefits depending on the plan.

For warranty support, customers should provide the order number, product serial number,
purchase date, description of the issue, and troubleshooting steps already attempted.
Support may request photos, diagnostic screenshots, or a short video showing the issue.

Smartphones with power, battery, charging, or display defects should first be checked
with the original charger and cable. If basic troubleshooting fails, support can start
a warranty claim or refer the customer to an authorized repair partner.
```

- [ ] **Step 4: Add `techstore_shipping.md`**

Create `docs/knowledge_base/techstore_shipping.md` with:

```markdown
# TechStore Plus Shipping Policy

TechStore Plus offers standard, expedited, and priority shipping in eligible regions.
Standard shipping usually arrives in 3 to 7 business days. Expedited shipping usually
arrives in 2 to 3 business days. Priority shipping usually arrives in 1 to 2 business
days when inventory is available and the order is placed before the daily cutoff time.

Large monitors, desktop computers, and home theater equipment may require extra handling
time. Some high-value products require adult signature confirmation at delivery.

Customers receive a tracking number by email when the order ships. If tracking has not
updated for more than 48 hours, support can investigate with the carrier.

If a package is marked delivered but the customer cannot find it, the customer should
check nearby doors, building reception, mailrooms, and neighbors before opening a case.
Missing delivery cases with urgent deadlines are routed to Priority Support.
```

- [ ] **Step 5: Add `techstore_products.md`**

Create `docs/knowledge_base/techstore_products.md` with:

```markdown
# TechStore Plus Product Knowledge

TechStore Plus sells laptops, smartphones, tablets, monitors, routers, smart home
devices, headphones, keyboards, mice, and home theater accessories.

Engineering students commonly choose laptops with at least 16 GB RAM, 512 GB SSD
storage, and a modern Intel Core i5, Intel Core i7, AMD Ryzen 5, AMD Ryzen 7, or Apple
Silicon processor. Customers using CAD, virtual machines, or data science tools should
consider 32 GB RAM when budget allows.

Gaming customers should prioritize a dedicated GPU, high-refresh display, strong cooling,
and at least 16 GB RAM. For competitive gaming, a 144 Hz or faster monitor is recommended.

Home office customers usually benefit from a reliable laptop or desktop, noise-canceling
headphones, an external monitor, ergonomic keyboard, wireless mouse, and a Wi-Fi 6 router.
```

- [ ] **Step 6: Add `techstore_support.md`**

Create `docs/knowledge_base/techstore_support.md` with:

```markdown
# TechStore Plus Support Policy

TechStore Plus support classifies customer requests as general information, product
inquiry, technical support, billing, returns, warranty, installation, financing, or
urgent priority support.

Priority Support is used when a customer reports a damaged delivery, missing package
with an urgent deadline, safety concern, repeated failed delivery, business-critical
device failure, or a high-value order at risk.

Support agents should ask for the customer's order number, product name, contact email,
and a concise description of the issue. For technical problems, agents should collect
the device model, operating system, error messages, and troubleshooting already tried.

When a request requires follow-up, support should create a task with the customer email,
issue summary, due date or urgency, and next action.
```

- [ ] **Step 7: Add `sample_external_document.txt`**

Create `docs/knowledge_base/sample_external_document.txt` with:

```text
External Reference: Home Office Setup Checklist

This sample external document is included to demonstrate TXT ingestion for the Week 4
RAG challenge. A reliable home office setup should include a primary computer, a backup
power plan, stable internet, secure Wi-Fi, an external display, and comfortable input
devices. Users who attend many video calls should also consider a dedicated webcam,
USB microphone, and noise-canceling headphones.
```

- [ ] **Step 8: Update `.gitignore`**

Append this section to `.gitignore`:

```gitignore

# Generated vector stores
chroma_db/
```

- [ ] **Step 9: Update `requirements.txt`**

Add these dependency lines if they are not already present:

```text
chromadb
langchain-community
langchain-text-splitters
pypdf
```

- [ ] **Step 10: Commit**

Run:

```powershell
git add docs/knowledge_base .gitignore requirements.txt
git commit -m "feat: add week 4 rag knowledge base"
```

Expected: commit succeeds with only the new knowledge-base files and metadata changes.

---

### Task 2: Implement Document Loading

**Files:**
- Create: `src/rag/__init__.py`
- Create: `src/rag/document_loader.py`
- Test: `tests/test_rag_document_loader.py`

- [ ] **Step 1: Write failing loader tests**

Create `tests/test_rag_document_loader.py`:

```python
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
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_rag_document_loader.py -v`

Expected: FAIL because `src.rag.document_loader` does not exist.

- [ ] **Step 3: Implement loader module**

Create `src/rag/__init__.py`:

```python
"""Retrieval-Augmented Generation utilities for TechStore Plus."""
```

Create `src/rag/document_loader.py`:

```python
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
```

- [ ] **Step 4: Run loader tests**

Run: `pytest tests/test_rag_document_loader.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/rag tests/test_rag_document_loader.py
git commit -m "feat: add rag document loader"
```

Expected: commit succeeds.

---

### Task 3: Implement Text Splitting

**Files:**
- Create: `src/rag/text_splitter.py`
- Test: `tests/test_rag_text_splitter.py`

- [ ] **Step 1: Write failing splitter tests**

Create `tests/test_rag_text_splitter.py`:

```python
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
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_rag_text_splitter.py -v`

Expected: FAIL because `src.rag.text_splitter` does not exist.

- [ ] **Step 3: Implement splitter module**

Create `src/rag/text_splitter.py`:

```python
from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 700
DEFAULT_CHUNK_OVERLAP = 120


def split_documents(
    documents: list[Document],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Split documents into searchable chunks while preserving metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata = {**chunk.metadata, "chunk_index": index}
    return chunks
```

- [ ] **Step 4: Run splitter tests**

Run: `pytest tests/test_rag_text_splitter.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/rag/text_splitter.py tests/test_rag_text_splitter.py
git commit -m "feat: add rag text splitter"
```

Expected: commit succeeds.

---

### Task 4: Implement Chroma Vector Store

**Files:**
- Create: `src/rag/vector_store.py`
- Test: `tests/test_rag_vector_store.py`

- [ ] **Step 1: Write failing vector-store tests**

Create `tests/test_rag_vector_store.py`:

```python
from langchain_core.documents import Document

from src.rag.vector_store import create_or_load_vector_store


class FakeEmbeddings:
    def embed_documents(self, texts):
        return [[float(len(text)), float(text.count("return"))] for text in texts]

    def embed_query(self, text):
        return [float(len(text)), float(text.count("return"))]


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
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_rag_vector_store.py -v`

Expected: FAIL because `src.rag.vector_store` does not exist or `chromadb` is not installed.

- [ ] **Step 3: Install/update dependencies if needed**

Run: `.venv\Scripts\python.exe -m pip install -r requirements.txt`

Expected: `chromadb`, `langchain-community`, `langchain-text-splitters`, and `pypdf` install successfully.

- [ ] **Step 4: Implement vector store module**

Create `src/rag/vector_store.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Protocol

import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


DEFAULT_PERSIST_DIRECTORY = Path("chroma_db/techstore_knowledge")
DEFAULT_COLLECTION_NAME = "techstore_knowledge"


class Embeddings(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


class LangChainEmbeddingFunction(EmbeddingFunction):
    def __init__(self, embeddings: Embeddings) -> None:
        self._embeddings = embeddings

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self._embeddings.embed_documents(input)


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
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=LangChainEmbeddingFunction(self.embeddings),
        )

    def add_documents(self, documents: list[Document]) -> None:
        if not documents:
            return

        ids = [_document_id(document, index) for index, document in enumerate(documents)]
        self._collection.upsert(
            ids=ids,
            documents=[document.page_content for document in documents],
            metadatas=[document.metadata for document in documents],
        )

    def similarity_search(self, query: str, *, k: int = 4) -> list[Document]:
        result = self._collection.query(query_texts=[query], n_results=k)
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
```

- [ ] **Step 5: Run vector-store tests**

Run: `pytest tests/test_rag_vector_store.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/rag/vector_store.py tests/test_rag_vector_store.py requirements.txt .gitignore
git commit -m "feat: add chroma rag vector store"
```

Expected: commit succeeds.

---

### Task 5: Implement RAG Chain

**Files:**
- Create: `src/rag/rag_chain.py`
- Modify: `src/rag/__init__.py`
- Test: `tests/test_rag_chain.py`

- [ ] **Step 1: Write failing RAG chain tests**

Create `tests/test_rag_chain.py`:

```python
from langchain_core.documents import Document

from src.rag.rag_chain import TechStoreRAGAssistant, should_use_rag


class FakeRetriever:
    def __init__(self, documents):
        self.documents = documents
        self.queries = []

    def similarity_search(self, query, *, k=4):
        self.queries.append((query, k))
        return self.documents


class FakeLLM:
    def __init__(self, content):
        self.content = content
        self.prompts = []

    def invoke(self, messages):
        self.prompts.append(messages)

        class Response:
            content = self.content

        return Response()


def test_should_use_rag_for_policy_questions():
    assert should_use_rag("What is the return window for laptops?")
    assert should_use_rag("How does smartphone warranty work?")
    assert should_use_rag("Which shipping options are available?")
    assert not should_use_rag("Please remember my email for later")


def test_rag_assistant_answers_with_sources():
    retriever = FakeRetriever(
        [
            Document(
                page_content="Returns are accepted within 30 calendar days.",
                metadata={"title": "techstore_returns.md", "source": "returns.md"},
            )
        ]
    )
    llm = FakeLLM("Customers can return most items within 30 days.")
    assistant = TechStoreRAGAssistant(retriever=retriever, llm=llm)

    answer = assistant.answer("What is the return window?")

    assert "Customers can return most items within 30 days." in answer
    assert "Sources: techstore_returns.md" in answer
    assert retriever.queries == [("What is the return window?", 4)]
    assert "Returns are accepted" in llm.prompts[0][0].content


def test_rag_assistant_returns_not_found_when_no_documents():
    assistant = TechStoreRAGAssistant(retriever=FakeRetriever([]), llm=FakeLLM("unused"))

    answer = assistant.answer("Do you repair espresso machines?")

    assert answer == "I could not find that answer in the TechStore knowledge base."
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_rag_chain.py -v`

Expected: FAIL because `src.rag.rag_chain` does not exist.

- [ ] **Step 3: Implement RAG chain module**

Create `src/rag/rag_chain.py`:

```python
from __future__ import annotations

from typing import Protocol

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


RAG_KEYWORDS = {
    "policy",
    "policies",
    "return",
    "returns",
    "refund",
    "exchange",
    "warranty",
    "shipping",
    "delivery",
    "damaged",
    "package",
    "product",
    "products",
    "support",
    "priority",
}


class Retriever(Protocol):
    def similarity_search(self, query: str, *, k: int = 4) -> list[Document]:
        ...


class LLM(Protocol):
    def invoke(self, messages: list[HumanMessage]):
        ...


def should_use_rag(user_text: str) -> bool:
    normalized = user_text.lower()
    return any(keyword in normalized for keyword in RAG_KEYWORDS)


class TechStoreRAGAssistant:
    def __init__(self, *, retriever: Retriever, llm: LLM | None = None, k: int = 4) -> None:
        self._retriever = retriever
        self._llm = llm or ChatOpenAI(model="gpt-4.1-mini", temperature=0)
        self._k = k

    def answer(self, question: str) -> str:
        documents = self._retriever.similarity_search(question, k=self._k)
        if not documents:
            return "I could not find that answer in the TechStore knowledge base."

        context = _format_context(documents)
        prompt = (
            "You are TechStore Plus support. Answer the customer's question using only "
            "the context below. If the context does not contain the answer, say you "
            "could not find the answer in the TechStore knowledge base.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}"
        )
        response = self._llm.invoke([HumanMessage(content=prompt)])
        answer_text = str(response.content).strip()
        sources = _format_sources(documents)
        return f"{answer_text}\n\nSources: {sources}"


def _format_context(documents: list[Document]) -> str:
    parts = []
    for index, document in enumerate(documents, start=1):
        title = document.metadata.get("title") or document.metadata.get("source", "Unknown source")
        parts.append(f"[{index}] {title}\n{document.page_content}")
    return "\n\n".join(parts)


def _format_sources(documents: list[Document]) -> str:
    sources = []
    for document in documents:
        source = document.metadata.get("title") or document.metadata.get("source", "Unknown source")
        if source not in sources:
            sources.append(str(source))
    return ", ".join(sources)
```

- [ ] **Step 4: Update public exports**

Modify `src/rag/__init__.py`:

```python
"""Retrieval-Augmented Generation utilities for TechStore Plus."""

from src.rag.rag_chain import TechStoreRAGAssistant, should_use_rag

__all__ = ["TechStoreRAGAssistant", "should_use_rag"]
```

- [ ] **Step 5: Run RAG chain tests**

Run: `pytest tests/test_rag_chain.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/rag/rag_chain.py src/rag/__init__.py tests/test_rag_chain.py
git commit -m "feat: add grounded rag assistant"
```

Expected: commit succeeds.

---

### Task 6: Integrate RAG With MemoryAgent

**Files:**
- Modify: `src/chains/memory_agent.py`
- Test: `tests/test_memory_agent_rag_unit.py`

- [ ] **Step 1: Write failing MemoryAgent RAG tests**

Create `tests/test_memory_agent_rag_unit.py`:

```python
from langchain_core.messages import AIMessage

from src.chains.memory_agent import MemoryAgent


class FakeGraphAgent:
    def __init__(self):
        self.calls = []

    def invoke(self, payload):
        self.calls.append(payload)
        return {"messages": [*payload["messages"], AIMessage(content="Fallback answer.")]}


class FakeRAGAssistant:
    def __init__(self):
        self.questions = []

    def answer(self, question):
        self.questions.append(question)
        return "RAG answer.\n\nSources: techstore_returns.md"


def build_agent(monkeypatch, rag_assistant=None):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    agent = MemoryAgent(rag_assistant=rag_assistant)
    agent._agent = FakeGraphAgent()
    return agent


def test_chat_uses_rag_for_policy_question(monkeypatch):
    rag_assistant = FakeRAGAssistant()
    agent = build_agent(monkeypatch, rag_assistant=rag_assistant)

    reply = agent.chat("customer@example.com", "What is the return window for laptops?")

    assert reply == "RAG answer.\n\nSources: techstore_returns.md"
    assert rag_assistant.questions == ["What is the return window for laptops?"]
    assert agent._agent.calls == []


def test_chat_falls_back_to_existing_agent_for_non_rag_question(monkeypatch):
    rag_assistant = FakeRAGAssistant()
    agent = build_agent(monkeypatch, rag_assistant=rag_assistant)

    reply = agent.chat("customer@example.com", "Please remember that I prefer email.")

    assert reply == "Fallback answer."
    assert rag_assistant.questions == []
    assert len(agent._agent.calls) == 1
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `pytest tests/test_memory_agent_rag_unit.py -v`

Expected: FAIL because `MemoryAgent` does not accept `rag_assistant`.

- [ ] **Step 3: Modify MemoryAgent imports and protocols**

Modify the imports in `src/chains/memory_agent.py`:

```python
from src.rag.rag_chain import TechStoreRAGAssistant, should_use_rag
```

Add this protocol below `TaskClient`:

```python
class RAGAssistant(Protocol):
    def answer(self, question: str) -> str:
        ...
```

- [ ] **Step 4: Modify MemoryAgent constructor**

Change the constructor signature and body:

```python
def __init__(
    self,
    task_client: TaskClient | None = None,
    rag_assistant: RAGAssistant | None = None,
) -> None:
    self._llm = ChatOpenAI(model=MODEL, temperature=0)
    self._agent = create_react_agent(self._llm, tools=TOOLS)
    self._memories: dict[str, HybridMemory] = {}
    self._task_client = task_client
    self._rag_assistant = rag_assistant
```

- [ ] **Step 5: Add RAG branch at the start of `chat` after storing user message**

Inside `chat`, after:

```python
memory = self._memory_for(customer_email)
memory.append_user(HumanMessage(content=user_text))
```

add:

```python
if self._rag_assistant is not None and should_use_rag(user_text):
    reply_text = self._rag_assistant.answer(user_text)
    memory.append_assistant(AIMessage(content=reply_text))
    return reply_text
```

Leave the existing LangGraph and Notion follow-up logic unchanged.

- [ ] **Step 6: Run integration tests**

Run:

```powershell
pytest tests/test_memory_agent_rag_unit.py c03-t05-bruno-pieri-m1-challenge/tests/test_memory_agent_followup_unit.py -v
```

Expected: PASS. Existing follow-up behavior still works.

- [ ] **Step 7: Commit**

Run:

```powershell
git add src/chains/memory_agent.py tests/test_memory_agent_rag_unit.py
git commit -m "feat: route techstore policy questions to rag"
```

Expected: commit succeeds.

---

### Task 7: Add Indexing Helper And Notebook Demonstration

**Files:**
- Create: `src/rag/index_knowledge_base.py`
- Create: `Week4_RAG_TechStore.ipynb`

- [ ] **Step 1: Create indexing helper**

Create `src/rag/index_knowledge_base.py`:

```python
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
```

- [ ] **Step 2: Create notebook with exact sections**

Create `Week4_RAG_TechStore.ipynb` with these markdown/code sections:

```markdown
# Week 4 - RAG Fundamentals with TechStore Plus

This notebook demonstrates the Week 4 RAG challenge using the existing TechStore
chatbot domain. It loads local documents, splits them into chunks, stores embeddings
in ChromaDB, reloads the vector store, and asks grounded questions.
```

Code cell:

```python
from pathlib import Path

from dotenv import load_dotenv

from src.rag.document_loader import load_documents
from src.rag.text_splitter import split_documents
from src.rag.vector_store import create_or_load_vector_store
from src.rag.rag_chain import TechStoreRAGAssistant

load_dotenv()

KNOWLEDGE_BASE = Path("docs/knowledge_base")
PERSIST_DIR = Path("chroma_db/techstore_knowledge")
COLLECTION = "techstore_knowledge"
```

Markdown cell:

```markdown
## 1. Load Documents
```

Code cell:

```python
documents = load_documents(KNOWLEDGE_BASE)
len(documents), [doc.metadata["title"] for doc in documents]
```

Markdown cell:

```markdown
## 2. Split Into Chunks
```

Code cell:

```python
chunks = split_documents(documents)
print(f"Generated {len(chunks)} chunks")
chunks[0]
```

Markdown cell:

```markdown
## 3. Generate Embeddings And Store In ChromaDB
```

Code cell:

```python
vector_store = create_or_load_vector_store(
    persist_directory=PERSIST_DIR,
    collection_name=COLLECTION,
)
vector_store.add_documents(chunks)
print(f"Persisted {len(chunks)} chunks in {PERSIST_DIR}")
```

Markdown cell:

```markdown
## 4. Reload And Retrieve
```

Code cell:

```python
reloaded_store = create_or_load_vector_store(
    persist_directory=PERSIST_DIR,
    collection_name=COLLECTION,
)
retrieved = reloaded_store.similarity_search("What is the return window for laptops?", k=3)
[(doc.metadata.get("title"), doc.page_content[:180]) for doc in retrieved]
```

Markdown cell:

```markdown
## 5. Ask Grounded Questions
```

Code cell:

```python
assistant = TechStoreRAGAssistant(retriever=reloaded_store)

questions = [
    "What is the return window for laptops?",
    "How does warranty coverage work for smartphones?",
    "What shipping options are available?",
    "What should I do if my order arrived damaged?",
]

for question in questions:
    print("=" * 80)
    print(question)
    print(assistant.answer(question))
```

- [ ] **Step 3: Run notebook smoke conversion**

Run: `.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute Week4_RAG_TechStore.ipynb --output Week4_RAG_TechStore.executed.ipynb`

Expected: PASS if `OPENAI_API_KEY` is configured. If no API key is configured, expected failure mentions missing OpenAI credentials; record this in the final implementation notes and do not commit the executed notebook.

- [ ] **Step 4: Commit**

Run:

```powershell
git add src/rag/index_knowledge_base.py Week4_RAG_TechStore.ipynb
git commit -m "feat: add week 4 rag notebook"
```

Expected: commit succeeds.

---

### Task 8: Document Week 4 In README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add README section**

Add this section after the Week 2 section or before Conversation Persistence:

```markdown
---

## Week 4 — RAG Fundamentals (`Week4_RAG_TechStore.ipynb`)

Week 4 adds Retrieval-Augmented Generation to the TechStore Plus chatbot without
replacing the previous weeks. The RAG pipeline loads TechStore knowledge-base documents,
splits them into chunks, stores embeddings in ChromaDB, reloads the persisted vector
store, and answers customer questions using retrieved context.

### Architecture

```text
docs/knowledge_base/*
  → src.rag.document_loader.load_documents()
  → src.rag.text_splitter.split_documents()
  → src.rag.vector_store.TechStoreVectorStore
  → ChromaDB persisted under chroma_db/
  → src.rag.rag_chain.TechStoreRAGAssistant
  → grounded answer with source metadata
```

### Running

```powershell
pip install -r requirements.txt
jupyter notebook Week4_RAG_TechStore.ipynb
```

Create a `.env` file with `OPENAI_API_KEY` before running embedding or answer cells.
Generated ChromaDB files are local artifacts and are ignored by Git.

### What Week 4 Adds

| Capability | Description |
|------------|-------------|
| Document loading | Supports `.md`, `.txt`, and `.pdf` files |
| Chunking | Uses recursive splitting with metadata preserved |
| Vector database | Persists embeddings in local ChromaDB |
| Grounded Q&A | Answers TechStore policy questions with retrieved context |
| Chatbot integration | Routes policy, warranty, shipping, returns, product, and support questions to RAG |
```

- [ ] **Step 2: Commit**

Run:

```powershell
git add README.md
git commit -m "docs: document week 4 rag workflow"
```

Expected: commit succeeds.

---

### Task 9: Final Verification

**Files:**
- All files changed by Tasks 1-8.

- [ ] **Step 1: Run Python unit tests**

Run:

```powershell
pytest tests/test_rag_document_loader.py tests/test_rag_text_splitter.py tests/test_rag_vector_store.py tests/test_rag_chain.py tests/test_memory_agent_rag_unit.py -v
```

Expected: PASS.

- [ ] **Step 2: Run existing relevant regression tests**

Run:

```powershell
pytest c03-t05-bruno-pieri-m1-challenge/tests/test_memory_agent_followup_unit.py backend/tests/test_chat_api.py -v
```

Expected: PASS.

- [ ] **Step 3: Run notebook check**

Run:

```powershell
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute Week4_RAG_TechStore.ipynb --output Week4_RAG_TechStore.executed.ipynb
```

Expected: PASS when `OPENAI_API_KEY` is configured. If it fails because no OpenAI key is available, run all non-notebook tests and record the credential limitation in the final response.

- [ ] **Step 4: Remove generated executed notebook if created**

Run:

```powershell
Remove-Item Week4_RAG_TechStore.executed.ipynb
```

Expected: generated execution artifact is removed.

- [ ] **Step 5: Confirm Git status**

Run: `git status --short`

Expected: only intentionally untracked local artifacts remain, such as pre-existing `.superpowers/` or `backups/`; no implementation files are unstaged.

- [ ] **Step 6: Final commit if verification changed docs or metadata**

If verification caused any intentional tracked changes, run:

```powershell
git add <changed-files>
git commit -m "chore: finalize week 4 rag verification"
```

Expected: no commit is needed unless a tracked file changed during verification.
