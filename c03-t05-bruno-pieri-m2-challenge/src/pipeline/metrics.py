"""
pipeline/metrics.py — Retrieval quality metrics for Stop 2 evaluation.

Position in the architecture:
    vectorstore.py (baseline or MMR)  →  [reranker.py]  →  metrics.py

Stop 2 (W5): Implement precision_at_k() and mrr() and use them to compare the
Stop 1 baseline retriever against the Stop 2 optimised pipeline.

METRIC DEFINITIONS
──────────────────
Precision@k
    Of the first k documents returned, what fraction are in the relevant set?
    Range [0, 1]. Higher is better. Penalises irrelevant documents at any rank.

MRR (Mean Reciprocal Rank)
    1 / rank_of_first_relevant_document. Range (0, 1].
    MRR = 1.0 if the first result is relevant; 0.5 if the second; 0.33 if third.
    Averaged across all queries. More sensitive than Precision@k to the position
    of the first hit — critical for customer support where users read top result first.

WHY BOTH METRICS?
    Precision@k rewards a pipeline that retrieves many relevant documents in the
    top-k window (important when the LLM needs broad context). MRR rewards getting
    the single most relevant document as early as possible (important for the
    cross-encoder, which must surface the best chunk in position 1 of 3).
    Together they give a fuller picture: a system with high MRR but low Precision@k
    is good at ranking but retrieves many irrelevant chunks alongside the best one.
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Core metric functions (match the Stop 2 challenge brief signatures)
# ---------------------------------------------------------------------------

def precision_at_k(retrieved: list[str], relevant: list[str], k: int) -> float:
    """Fraction of the top-k retrieved documents that are in the relevant set.

    Args:
        retrieved: Ordered list of retrieved document identifiers (e.g. filenames),
                   most relevant first.
        relevant:  Ground-truth set of relevant document identifiers for this query.
        k:         Cut-off rank.

    Returns:
        Float in [0, 1].

    Example::

        precision_at_k(
            retrieved=["a.txt", "b.txt", "c.txt"],
            relevant=["a.txt", "c.txt"],
            k=3,
        )
        # → 0.667  (2 of the top-3 are relevant)
    """
    if k <= 0:
        raise ValueError("k must be >= 1")
    hits = set(retrieved[:k]) & set(relevant)
    return len(hits) / k


def mrr(retrieved: list[str], relevant: list[str]) -> float:
    """Mean Reciprocal Rank: 1 / rank of the first relevant document.

    If no relevant document appears in *retrieved*, returns 0.0.

    Args:
        retrieved: Ordered list of retrieved document identifiers, most relevant first.
        relevant:  Ground-truth set of relevant document identifiers.

    Returns:
        Float in [0, 1].

    Example::

        mrr(retrieved=["b.txt", "a.txt", "c.txt"], relevant=["a.txt"])
        # → 0.5  (first relevant doc is at rank 2)
    """
    relevant_set = set(relevant)
    for i, doc_id in enumerate(retrieved):
        if doc_id in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

@dataclass
class QueryResult:
    """Per-query metric result."""
    query: str
    retrieved_sources: list[str]
    relevant_sources: list[str]
    precision_at_3: float
    precision_at_6: float
    mrr_score: float


def evaluate_retriever(
    retriever_fn,
    eval_set: list[dict],
    *,
    k_values: tuple[int, ...] = (3, 6),
) -> tuple[list[QueryResult], dict[str, float]]:
    """Run *retriever_fn* over *eval_set* and compute Precision@k and MRR.

    Args:
        retriever_fn: Callable[str, list[Document]] — takes a query string and
                      returns an ordered list of LangChain Documents.
        eval_set:     List of dicts with keys:
                      - ``"query"`` (str)
                      - ``"relevant"`` (list[str], known-relevant filenames)
        k_values:     Tuple of k values for Precision@k.  Default (3, 6).

    Returns:
        Tuple of:
        - list of :class:`QueryResult` (one per query)
        - dict with aggregate metrics: ``"precision@3"``, ``"precision@6"``, ``"mrr"``

    Example::

        results, agg = evaluate_retriever(
            retriever_fn=lambda q: retriever.invoke(q),
            eval_set=EVAL_SET,
        )
        print(f"MRR: {agg['mrr']:.2f}")
    """
    query_results: list[QueryResult] = []

    for item in eval_set:
        query = item["query"]
        relevant = item["relevant"]

        docs = retriever_fn(query)
        sources = [doc.metadata.get("source", "") for doc in docs]

        p3 = precision_at_k(sources, relevant, k=3) if len(sources) >= 3 else precision_at_k(sources, relevant, k=len(sources))
        p6 = precision_at_k(sources, relevant, k=6) if len(sources) >= 6 else precision_at_k(sources, relevant, k=len(sources))
        mrr_score = mrr(sources, relevant)

        query_results.append(QueryResult(
            query=query,
            retrieved_sources=sources,
            relevant_sources=relevant,
            precision_at_3=p3,
            precision_at_6=p6,
            mrr_score=mrr_score,
        ))

    n = len(query_results)
    aggregate = {
        "precision@3": sum(r.precision_at_3 for r in query_results) / n,
        "precision@6": sum(r.precision_at_6 for r in query_results) / n,
        "mrr": sum(r.mrr_score for r in query_results) / n,
    }
    return query_results, aggregate


# ---------------------------------------------------------------------------
# Ground-truth evaluation set (10 queries, Stop 2 Component 4)
# ---------------------------------------------------------------------------

EVAL_SET: list[dict] = [
    {
        "query": "What is the return window for a refund?",
        "relevant": ["policy_return_policy.txt"],
    },
    {
        "query": "How do I reset the Router NX300?",
        "relevant": ["product_manual_router_nx300.txt", "support_router_wont_connect.txt"],
    },
    {
        "query": "What does the Premium Protection Plan cover?",
        "relevant": ["policy_warranty_terms.txt"],
    },
    {
        "query": "Steps to file a warranty claim online",
        "relevant": ["support_warranty_claim_process.txt"],
    },
    {
        "query": "Laptop Pro X1 specifications",
        "relevant": ["product_manual_laptop_pro_x1.txt"],
    },
    {
        "query": "How do I pair a Zigbee device with the Smart Hub?",
        "relevant": ["product_manual_smart_hub_home.txt"],
    },
    {
        "query": "Does TechStore Plus cover accidental damage?",
        "relevant": ["policy_warranty_terms.txt"],
    },
    {
        "query": "Laptop won't turn on — first troubleshooting step",
        "relevant": ["support_laptop_wont_power_on.txt"],
    },
    {
        "query": "What is the restocking fee for an opened product?",
        "relevant": ["policy_return_policy.txt"],
    },
    {
        "query": "Warranty period for networking equipment",
        "relevant": ["policy_warranty_terms.txt", "product_manual_router_nx300.txt"],
    },
]
