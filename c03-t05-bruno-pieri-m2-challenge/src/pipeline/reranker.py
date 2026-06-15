"""
pipeline/reranker.py — Cross-encoder re-ranking stage.

Position in the architecture:
    vectorstore.py (MMR retriever)  →  reranker.py  →  LLM context window

Stop 2 (W5): Implement rerank().

WHY CROSS-ENCODER AFTER RETRIEVAL (for your docstring)?
    The MMR retriever uses a bi-encoder: query and document are embedded
    *separately*, then compared by cosine similarity.  This is fast (O(1) per
    query after indexing) but lossy — the embeddings compress meaning into fixed
    vectors and cannot model fine-grained query-document interactions.

    A cross-encoder processes (query, document) *together* through a transformer,
    capturing cross-attention between every query token and every document token.
    This is much more accurate at ranking relevant documents, but too slow to run
    over an entire corpus — hence we run it only over the small MMR candidate set
    (fetch_k=20 → k=6 → reranked top-3).

    This two-stage pattern (fast bi-encoder retrieval + precise cross-encoder
    re-ranking) is the standard production pattern for neural retrieval.

WHY RERANK ONLY THE TOP-6 AND NOT ALL DOCUMENTS?
    The cross-encoder is O(n) in the number of candidates (one forward pass per
    pair).  Running it over all corpus chunks would be prohibitively slow.
    MMR acts as a fast pre-filter, and the cross-encoder precision-sorts the
    survivors.  The final context window receives only RERANK_TOP_N=3 chunks
    to avoid context length inflation.
"""

from __future__ import annotations

from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RERANK_TOP_N: int = 3
"""Number of documents returned to the LLM after re-ranking.

Keeping the context to 3 chunks limits token usage and forces the cross-encoder
to select only the most relevant evidence, improving answer precision.
"""

_CROSS_ENCODER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
"""HuggingFace cross-encoder model for re-ranking.

``ms-marco-MiniLM-L-6-v2`` is trained on the MS MARCO passage ranking dataset —
question-answer pairs similar to customer support queries.  It is fast (6-layer
MiniLM) and accurate enough for this use case.  For higher accuracy at the cost
of latency, consider ``cross-encoder/ms-marco-electra-base``.
"""

# Module-level singleton — loaded once to avoid reloading the model on every call.
_cross_encoder = None


def rerank(
    query: str,
    docs: list[Document],
    top_n: int = RERANK_TOP_N,
) -> list[Document]:
    """Re-rank *docs* against *query* using a cross-encoder and return the top *top_n*.

    The cross-encoder (``cross-encoder/ms-marco-MiniLM-L-6-v2``) takes
    (query, document_text) pairs and outputs a relevance score.  Documents are
    sorted descending by score; only the top *top_n* are returned.

    WHY CROSS-ENCODING IS MORE ACCURATE THAN BI-ENCODER COSINE SIMILARITY:
        A bi-encoder embeds query and document independently and compares them in
        a shared vector space — fast, but lossy.  A cross-encoder processes the
        (query, document) pair *jointly* through a full transformer, enabling
        cross-attention between every query token and every document token.  This
        captures precise lexical and semantic interactions that are invisible to
        independent embeddings.  The cost is one forward pass per candidate pair,
        so cross-encoders are used only on the small MMR shortlist (k=6), not on
        the full corpus.

    The downstream RAG chain interface does not change: it still receives a list
    of Documents, just a smaller and more relevant one.

    Args:
        query:  The user's question string.
        docs:   Candidate documents from the MMR retriever
                (typically :data:`~src.pipeline.vectorstore.MMR_K` = 6 items).
        top_n:  Number of documents to return.  Defaults to :data:`RERANK_TOP_N`.

    Returns:
        A list of at most *top_n* Documents, sorted by decreasing relevance score.
        Each Document has a ``rerank_score`` entry added to its metadata.

    Raises:
        ValueError: If *docs* is empty or *top_n* < 1.

    Example::

        from src.pipeline.reranker import rerank

        mmr_results = retriever.invoke("warranty coverage for accidental damage")
        final_docs  = rerank("warranty coverage for accidental damage", mmr_results)
        assert len(final_docs) <= RERANK_TOP_N
    """
    if not docs:
        raise ValueError("docs must be non-empty")
    if top_n < 1:
        raise ValueError("top_n must be >= 1")

    global _cross_encoder
    if _cross_encoder is None:
        from sentence_transformers import CrossEncoder
        _cross_encoder = CrossEncoder(_CROSS_ENCODER_MODEL)

    pairs = [(query, doc.page_content) for doc in docs]
    scores = _cross_encoder.predict(pairs)

    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)

    result = []
    for score, doc in ranked[:top_n]:
        doc.metadata["rerank_score"] = float(score)
        result.append(doc)
    return result
