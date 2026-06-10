# Week 4 RAG TechStore Design

## Context

The Week 4 challenge asks for an end-to-end Retrieval-Augmented Generation pipeline:

- Load a document from PDF, TXT, or similar sources.
- Split the text into coherent chunks with metadata.
- Generate embeddings.
- Persist the vectors in ChromaDB.
- Reload the vector store and answer questions using retrieved context.
- Optionally build a chatbot over Python library documentation and evaluate retrieval quality.

The existing TechStore project already contains the Week 1 and Week 2 notebooks, memory/tooling work for Week 3, and a FastAPI/Next.js demo. Week 4 should extend that work without replacing or deleting previous deliverables.

## Goal

Add RAG as a new capability for the TechStore chatbot. The chatbot should be able to answer questions grounded in TechStore knowledge-base documents and also demonstrate ingestion of an external PDF or TXT document.

The implementation should preserve Weeks 1-3 and make Week 4 easy to present as a standalone learning milestone.

## Recommended Approach

Use a hybrid implementation:

- Reusable Python modules under `src/rag/`.
- TechStore knowledge-base documents under `docs/knowledge_base/`.
- A persisted local ChromaDB collection under `chroma_db/`.
- A Week 4 notebook that demonstrates ingestion, chunking, vector storage, retrieval, and grounded Q&A.
- A light integration point with the existing chatbot path, so RAG can complement the existing memory/tool agent without forcing a major rewrite.

## Scope

In scope:

- Create sample TechStore documents covering returns, warranty, shipping, products, and support policies.
- Support ingesting `.md`, `.txt`, and PDF files where dependencies are available.
- Split documents using LangChain text splitters.
- Store chunks and metadata in ChromaDB.
- Reload the persisted vector store without reprocessing documents.
- Build a simple RAG chain that retrieves relevant chunks and answers with citations/source metadata.
- Provide a notebook demonstration for the Week 4 challenge.
- Add focused tests for chunking, metadata handling, and retrieval behavior using mocked or deterministic components.

Out of scope:

- Replacing the Week 1 or Week 2 notebooks.
- Removing the Week 3 memory/tools implementation.
- Building a full document-upload UI.
- Large frontend redesign.
- Production-grade evaluation dashboards.

## Proposed File Layout

```text
docs/knowledge_base/
  techstore_returns.md
  techstore_warranty.md
  techstore_shipping.md
  techstore_products.md
  techstore_support.md
  sample_external_document.txt

src/rag/
  __init__.py
  document_loader.py
  text_splitter.py
  vector_store.py
  rag_chain.py

chroma_db/
  techstore_knowledge/

Week4_RAG_TechStore.ipynb
```

The exact ChromaDB contents should be generated locally and ignored by Git if the directory contains machine-specific database files.

## Architecture

```text
TechStore docs / PDF / TXT
  -> document_loader
  -> text_splitter
  -> vector_store indexing
  -> ChromaDB persisted collection
  -> retriever
  -> RAG prompt with retrieved context
  -> grounded answer with source metadata
```

### Document Loader

`document_loader.py` should provide a small interface for loading local files. Each loaded document should include:

- page content
- source path
- document title or filename
- page number when available
- document type

For PDFs, prefer LangChain's `PyPDFLoader` or a compatible loader already supported by the environment. If PDF dependencies are missing, TXT/MD support is still enough for the core TechStore documents, and the notebook can clearly explain the optional PDF path.

### Text Splitter

`text_splitter.py` should wrap `RecursiveCharacterTextSplitter` with defaults suitable for the challenge:

- chunk size around 500-800 characters or tokens
- overlap around 80-150 characters
- metadata preserved on every chunk

The notebook should print a small sample list of chunks to satisfy the first challenge deliverable.

### Vector Store

`vector_store.py` should handle:

- creating or loading the Chroma collection
- embedding documents
- persisting vectors locally
- exposing a retriever interface

Use OpenAI embeddings if `OPENAI_API_KEY` is configured. If a local embedding fallback is added, it should be optional and documented because it may add heavier dependencies.

### RAG Chain

`rag_chain.py` should expose a simple function or class for question answering:

```text
question -> retrieve relevant chunks -> compose grounded prompt -> LLM answer
```

Answers should:

- use only retrieved context when possible
- say when the answer is not available in the documents
- include source names or titles from metadata

## Chatbot Integration

The first integration should be lightweight:

- Keep the current `MemoryAgent` behavior intact.
- Add a RAG helper that can answer knowledge-base questions.
- Route document-grounded questions to RAG when they are about policy, warranty, shipping, returns, products, or support details.
- Fall back to the existing agent behavior for general conversation or workflow/tool tasks.

This keeps Week 4 additive instead of turning it into a risky rewrite.

## Notebook Demonstration

`Week4_RAG_TechStore.ipynb` should demonstrate:

1. Loading TechStore documents and one external TXT/PDF example.
2. Splitting into chunks with metadata.
3. Creating embeddings and saving to ChromaDB.
4. Reloading the vector store.
5. Asking sample questions:
   - "What is the return window for laptops?"
   - "How does warranty coverage work for smartphones?"
   - "What shipping options are available?"
   - "What should I do if my order arrived damaged?"
6. Showing retrieved sources for at least one answer.

## Testing

Add focused tests:

- Loader returns documents with source metadata.
- Splitter preserves metadata across chunks.
- RAG retrieval returns relevant chunks for known TechStore policy questions.
- RAG chain handles "not found in documents" cases gracefully.

Tests should avoid real OpenAI calls by using deterministic fake embeddings or small mocked components.

## Risks and Constraints

- ChromaDB and PDF loader dependencies may not be installed yet.
- Real OpenAI embeddings require `OPENAI_API_KEY`.
- Persisted vector stores are generated artifacts and may not be portable across machines.
- Current project has both notebook and backend/frontend paths, so the Week 4 integration should avoid broad rewrites.

## Acceptance Criteria

- Existing Week 1-3 files remain intact.
- TechStore knowledge-base documents exist and can be indexed.
- A local ChromaDB vector store can be created and reloaded.
- A notebook demonstrates all main challenge deliverables.
- The RAG chain returns grounded answers with source metadata.
- The existing chatbot can use RAG for TechStore knowledge questions.
- Tests or mock checks cover the core non-LLM logic.
