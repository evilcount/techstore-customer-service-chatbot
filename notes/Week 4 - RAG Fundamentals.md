---
week: 4
status: completed
tags:
  - rag
  - embeddings
  - chromadb
---

# Week 4 - RAG Fundamentals

## Objective

Build a basic end-to-end RAG pipeline for the TechStore Plus chatbot.

## Implemented

- Loading of PDF and TXT documents
- Text extraction with source and page metadata
- Text splitting with `RecursiveCharacterTextSplitter`
- OpenAI embeddings
- Persistent storage with ChromaDB
- Similarity search
- RAG answer generation
- Python `requests` documentation chatbot

## Chunk configuration

- Chunk size: 500
- Chunk overlap: 50

## Main files

- `Week4_RAG_TechStore.ipynb`
- `Week4_RAG_Python_Library.ipynb`
- `src/pipeline/loader.py`
- `src/pipeline/vectorstore.py`

## Architecture

[[Document Loading and Chunking]] → [[ChromaDB Vector Store]] → RAG answer

## Evolution

The basic retriever was optimized in [[Week 5 - RAG Optimization]].

## Related notes

- [[Document Loading and Chunking]]
- [[ChromaDB Vector Store]]
- [[Week 5 - RAG Optimization]]