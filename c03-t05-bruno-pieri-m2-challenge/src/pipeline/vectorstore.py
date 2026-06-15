"""
pipeline/vectorstore.py — ChromaDB setup and MMR retriever.

Position in the architecture:
    loader.py  →  vectorstore.py  →  reranker.py  →  LLM

Stop 1 (W4): Implement build_vectorstore() and load_vectorstore().
Stop 2 (W5): Implement get_mmr_retriever() — replace the default k-NN retriever
             with Maximal Marginal Relevance (MMR).

WHY MMR (for your Stop 2 docstring)?
    Standard similarity search ranks candidates by cosine similarity to the query.
    If the corpus has multiple nearly-identical chunks (e.g., three chunks from the
    same warranty document), all three may rank in the top-4, wasting the context
    window with redundant text.

    MMR solves this by balancing relevance against diversity: the i-th selected
    document maximises a linear combination of (similarity to query) and
    (dissimilarity to already-selected documents).  Setting fetch_k >> k gives
    the algorithm enough candidates to find both relevant *and* diverse results.

    Trade-off: MMR is slightly slower than k-NN similarity (extra pairwise
    comparisons) and can reduce recall on very narrow queries where all top
    results are from the same small document.  In the TechStore Plus corpus the
    diversity benefit outweighs this risk.
"""

from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_openai import OpenAIEmbeddings

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CHROMA_DIR: str = "./chroma_db"
"""Persist directory for the ChromaDB collection."""

COLLECTION_NAME: str = "techstore_docs"
"""ChromaDB collection name — keep consistent across build and load."""

MMR_K: int = 6
"""Number of documents the MMR retriever returns to the re-ranker.

We pass more documents than the final context window (RERANK_TOP_N in
reranker.py) so the cross-encoder has a larger candidate pool to precision-sort.
"""

MMR_FETCH_K: int = 20
"""Candidate pool size for MMR.

MMR internally scores all fetch_k candidates, then greedily selects k of them.
A larger fetch_k gives more diversity options but increases latency linearly.
20 is a practical default for corpora under 10,000 chunks.
"""


def _get_embeddings() -> OpenAIEmbeddings:
    """Return the shared OpenAI embeddings model.

    Uses ``text-embedding-3-small`` — the cheapest OpenAI embedding model
    that outperforms ``ada-002`` on MTEB benchmarks.  Do not swap for a
    HuggingFace model without updating the stored Chroma collection, as
    embeddings are not cross-compatible.
    """
    return OpenAIEmbeddings(model="text-embedding-3-small")


def build_vectorstore(chunks: list[Document]) -> Chroma:
    """Embed *chunks* and persist a ChromaDB collection to :data:`CHROMA_DIR`.

    On the first run this calls the OpenAI embeddings API.  On subsequent runs,
    call :func:`load_vectorstore` instead — it reads from disk without API calls.

    The collection uses cosine similarity (ChromaDB default).

    Args:
        chunks: Output of :func:`~src.pipeline.loader.chunk_documents`.

    Returns:
        A :class:`~langchain_chroma.Chroma` vectorstore instance.

    Raises:
        ValueError: If *chunks* is empty.
        openai.AuthenticationError: If ``OPENAI_API_KEY`` is not set.

    Example::

        from src.pipeline.loader import load_documents, chunk_documents
        from src.pipeline.vectorstore import build_vectorstore

        docs = load_documents()
        chunks = chunk_documents(docs)
        vs = build_vectorstore(chunks)
        print(f"Stored {vs._collection.count()} embeddings")
    """
    if not chunks:
        raise ValueError("chunks must be non-empty — load and chunk documents first.")

    vs = Chroma.from_documents(
        documents=chunks,
        embedding=_get_embeddings(),
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
    )
    print(f"Built vectorstore with {len(chunks)} chunks at {CHROMA_DIR}")
    return vs


def load_vectorstore() -> Chroma:
    """Load an existing ChromaDB collection from :data:`CHROMA_DIR`.

    Does NOT call the embeddings API — reads pre-computed vectors from disk.
    Call this on every run after the initial :func:`build_vectorstore` call.

    Returns:
        A :class:`~langchain_chroma.Chroma` vectorstore instance.

    Raises:
        FileNotFoundError: If ``CHROMA_DIR`` does not exist or is empty.

    Example::

        vs = load_vectorstore()
        docs = vs.similarity_search("return policy", k=4)
    """
    chroma_path = Path(CHROMA_DIR)
    if not chroma_path.exists():
        raise FileNotFoundError(
            f"ChromaDB directory not found: {CHROMA_DIR}. "
            "Run build_vectorstore(chunk_documents(load_documents())) first."
        )

    vs = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=_get_embeddings(),
        collection_name=COLLECTION_NAME,
    )
    count = vs._collection.count()
    print(f"Loaded vectorstore from {CHROMA_DIR} ({count} chunks)")
    return vs


def get_mmr_retriever(vectorstore: Chroma) -> BaseRetriever:
    """Wrap *vectorstore* in an MMR retriever.

    WHY MMR (not simple similarity)?
        Similarity search returns the top-k closest vectors.  In a corpus where
        warranty terms appear in both ``policy_warranty_terms.txt`` and each
        product manual, all top-k results may be warranty chunks — the LLM
        receives redundant context and misses more specific product information.

        MMR selects the first document by pure similarity, then each subsequent
        document by the trade-off:
            ``lambda * sim(d, q) - (1 - lambda) * max_sim(d, selected)``
        With the default lambda=0.5, relevance and diversity are weighted equally.
        With fetch_k=20 >> k=6, MMR has enough candidates to find diverse results.

    Args:
        vectorstore: An initialised :class:`~langchain_chroma.Chroma` instance.

    Returns:
        A :class:`~langchain_core.retrievers.BaseRetriever` configured for MMR.

    Example::

        retriever = get_mmr_retriever(vs)
        results = retriever.invoke("laptop warranty")
        assert len(results) == MMR_K
    """
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": MMR_K, "fetch_k": MMR_FETCH_K},
    )
