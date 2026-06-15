"""
guardrails/writer.py — Citation-binding writer prompt.

Position in the architecture:
    reranker.py (top-3 docs) + graph snippets  →  writer.py  →  verifier.py

Stop 3 (W6): Implement build_cited_answer().

WHY CITATION BINDING (for your docstring)?
    Requiring inline citations ([key]) serves two purposes:
    1. User trust: readers can verify which source backs each claim.
    2. Verifiability: verifier.py uses the [key] annotations to look up the
       exact source chunk for each claim and run entailment checks.

    Without citation binding, the verifier would have to try every source chunk
    against every claim — O(claims × chunks).  With binding, it is O(claims).

    Citation format: [source_filename] for vector-store chunks,
                     [G:subject→object] for graph-sourced snippets,
                     [TB:filename:rowN] for table retrieval results.
"""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

_LLM_MODEL: str = "gpt-4.1-mini"


def build_cited_answer(
    question: str,
    context_docs: list[Document],
) -> str:
    """Generate a cited answer grounded in *context_docs*.

    Every sentence in the answer must end with an inline citation of the form
    ``[source_filename]`` where ``source_filename`` is the ``source`` metadata
    field of the most relevant context document for that sentence.

    WHY CITATION BINDING?
        Inline citations serve dual purpose: they let users verify each claim
        against the source document, and they allow verifier.py to perform
        O(claims) entailment checks by looking up only the cited source rather
        than comparing every claim against every chunk — O(claims × chunks).

    The writer prompt instructs the LLM to:
    - Use ONLY information present in *context_docs*.
    - End every sentence with ``[source_filename]``.
    - If the answer is not in the context, output exactly:
      ``"I don't have that information in our documentation."``
    - Never invent facts, model numbers, prices, or dates not in the context.

    Args:
        question:     The user's question.
        context_docs: The final context documents (typically top-3 from
                      :func:`~src.pipeline.reranker.rerank` plus any graph
                      snippets serialised as Documents).

    Returns:
        A string answer with inline ``[source_filename]`` citations.

    Raises:
        ValueError: If *context_docs* is empty.
        openai.AuthenticationError: If ``OPENAI_API_KEY`` is not set.

    Example::

        answer = build_cited_answer(
            "What is the return window for a refund?",
            top_docs,
        )
        # "You have 7 days from the delivery date to request a refund. [policy_return_policy.txt]"
    """
    if not context_docs:
        raise ValueError("context_docs must be non-empty")

    # Build a context block: each doc prefixed by its source key
    parts: list[str] = []
    for doc in context_docs:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[{source}]\n{doc.page_content}")
    context_str = "\n---\n".join(parts)

    prompt = (
        "You are a TechStore Plus support assistant. "
        "Answer the customer's question using ONLY the context below. "
        "Every sentence in your answer MUST end with [source_filename], "
        "where source_filename is the exact key shown in brackets before each context block "
        "(e.g. [policy_return_policy.txt] or [G:Laptop Pro X1->Premium Protection Plan]). "
        "If the answer to the question is NOT present in the context, output exactly:\n"
        "I don't have that information in our documentation.\n\n"
        "Never invent facts, model numbers, prices, or dates that are not in the context.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {question}\n\nAnswer:"
    )

    llm = ChatOpenAI(model=_LLM_MODEL, temperature=0)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
