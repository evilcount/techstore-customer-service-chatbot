"""
guardrails/verifier.py — Claim decomposition, entailment check, and decision gate.

Position in the architecture:
    writer.py (cited answer)  →  verifier.py  →  TechStoreRAGAgent (final answer)

Stop 3 (W6): Implement verify_answer().

DECISION GATE LOGIC (implement exactly as specified):
    If claim_support_rate >= 0.85:
        return GuardrailedAnswer(decision="answer", ...)

    If claim_support_rate < 0.85 AND contradiction_rate == 0:
        return GuardrailedAnswer(decision="answer_with_disclaimer", ...)

    If contradiction_rate > 0:
        return GuardrailedAnswer(decision="extractive", answer=most_relevant_chunk)

    If no relevant evidence exists (context_docs is empty OR all claims are "unknown"):
        return GuardrailedAnswer(decision="no_answer",
                                 answer="I don't have that information in our documentation.")

WHY THESE THRESHOLDS?
    0.85 support rate: allows minor contextual inferences while blocking
    answers where fewer than 85% of claims are verifiably grounded.

    contradiction_rate > 0: even a single contradiction (LLM asserted X,
    source says not-X) triggers extractive fallback because the answer is
    actively misleading, not merely unverified.

    extractive fallback returns the verbatim most-relevant chunk so the user
    gets accurate information without the risk of a generated misstatement.
"""

from __future__ import annotations

import json
import re

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.rag_agent import GuardrailedAnswer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SUPPORT_RATE_THRESHOLD: float = 0.85
"""Minimum fraction of claims that must be supported for a clean answer.

Tuning guide:
    0.95 — very conservative; suits high-stakes legal or medical contexts.
    0.85 — balanced default for e-commerce customer support.
    0.70 — lenient; acceptable for low-risk informational queries.
"""

_LLM_MODEL: str = "gpt-4.1-mini"

_NO_ANSWER_STRING: str = "I don't have that information in our documentation."
_CITATION_PATTERN = re.compile(r"\[[^\]]+\]")
_NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\b")


def citation_density(answer: str) -> float:
    """Return the fraction of sentences that contain at least one bracket citation."""
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", answer.strip())
        if sentence.strip()
    ]
    if not sentences:
        return 0.0
    cited = sum(1 for sentence in sentences if _CITATION_PATTERN.search(sentence))
    return cited / len(sentences)


def numeric_grounding_rate(answer: str, context_text: str) -> float:
    """Return the fraction of numbers in the answer that also appear in context."""
    answer_numbers = _NUMBER_PATTERN.findall(answer)
    if not answer_numbers:
        return 1.0
    context_numbers = set(_NUMBER_PATTERN.findall(context_text))
    grounded = sum(1 for number in answer_numbers if number in context_numbers)
    return grounded / len(answer_numbers)


def verify_answer(
    answer: str,
    context: list[Document],
) -> GuardrailedAnswer:
    """Decompose *answer* into atomic claims, verify each against *context*, apply gate.

    Verification procedure:
    1. Use an LLM to decompose *answer* into a list of atomic claims
       (one factual statement per item, no compound claims).
    2. For each claim, use a second LLM call with an entailment prompt:
       "Does the following passage SUPPORT, CONTRADICT, or is it UNKNOWN
        regarding this claim?"
       Map the response to one of ``{"supported", "contradicted", "unknown"}``.
    3. Compute:
       - ``claim_support_rate``   = supported_count / total_claims
       - ``contradiction_rate``   = contradicted_count / total_claims
    4. Apply the decision gate (see module-level docstring).
    5. Collect source filenames from context_docs metadata into ``cited_sources``.

    Args:
        answer:  The raw cited answer string from
                 :func:`~src.guardrails.writer.build_cited_answer`.
        context: The context documents used to generate *answer*.

    Returns:
        A fully populated :class:`~src.rag_agent.GuardrailedAnswer` instance.

    Raises:
        ValueError: If *answer* is an empty string.
        openai.AuthenticationError: If ``OPENAI_API_KEY`` is not set.

    Example::

        result = verify_answer(raw_answer, context_docs)
        if result.decision == "no_answer":
            print("No grounded evidence found.")
        elif result.decision == "answer_with_disclaimer":
            print(result.answer + "\\n[Note: some claims could not be verified]")
        else:
            print(result.answer)
    """
    if not answer:
        raise ValueError("answer must be non-empty")

    # Edge case: empty context → no_answer immediately
    if not context:
        return GuardrailedAnswer(
            answer=_NO_ANSWER_STRING,
            decision="no_answer",
            claim_support_rate=0.0,
            contradiction_rate=0.0,
            cited_sources=[],
        )

    # Edge case: writer already returned the no-answer sentinel
    if answer.strip() == _NO_ANSWER_STRING:
        return GuardrailedAnswer(
            answer=_NO_ANSWER_STRING,
            decision="no_answer",
            claim_support_rate=0.0,
            contradiction_rate=0.0,
            cited_sources=[],
        )

    llm = ChatOpenAI(model=_LLM_MODEL, temperature=0)

    # ------------------------------------------------------------------
    # Step 1: Decompose answer into atomic claims
    # ------------------------------------------------------------------
    decompose_prompt = (
        "Decompose the following answer into a JSON array of atomic claims. "
        "Each element must be a single, simple factual statement (no conjunctions). "
        "Return ONLY a valid JSON array of strings — no markdown, no explanation.\n\n"
        f"Answer: {answer}"
    )

    try:
        resp = llm.invoke([HumanMessage(content=decompose_prompt)])
        content = resp.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
        claims: list[str] = json.loads(content)
        if not isinstance(claims, list):
            claims = [answer]
    except Exception:
        claims = [answer]

    if not claims:
        return GuardrailedAnswer(
            answer=_NO_ANSWER_STRING,
            decision="no_answer",
            claim_support_rate=0.0,
            contradiction_rate=0.0,
            cited_sources=[],
        )

    # ------------------------------------------------------------------
    # Step 2: Entailment check for each claim
    # ------------------------------------------------------------------
    context_text = "\n---\n".join(doc.page_content for doc in context)[:4000]

    supported = 0
    contradicted = 0

    for claim in claims:
        entail_prompt = (
            "Given the passage below, does it SUPPORT, CONTRADICT, or is it UNKNOWN "
            "regarding the claim?\n"
            "Respond with exactly one word: SUPPORT, CONTRADICT, or UNKNOWN.\n\n"
            f"Claim: {claim}\n\n"
            f"Passage:\n{context_text}"
        )
        try:
            resp = llm.invoke([HumanMessage(content=entail_prompt)])
            label = resp.content.strip().upper()
            if "SUPPORT" in label:
                supported += 1
            elif "CONTRADICT" in label:
                contradicted += 1
            # UNKNOWN: neither counter incremented
        except Exception:
            pass

    total = max(len(claims), 1)
    claim_support_rate = supported / total
    contradiction_rate = contradicted / total

    # ------------------------------------------------------------------
    # Step 3: Collect cited sources (deduplicated)
    # ------------------------------------------------------------------
    cited_sources: list[str] = []
    for doc in context:
        src = (
            doc.metadata.get("table_citation")
            or doc.metadata.get("source")
            or ""
        )
        if src and src not in cited_sources:
            cited_sources.append(src)

    # ------------------------------------------------------------------
    # Step 4: Select most-relevant chunk for extractive fallback
    # ------------------------------------------------------------------
    best_chunk = max(
        context,
        key=lambda d: d.metadata.get("rerank_score", 0.0),
    )

    # ------------------------------------------------------------------
    # Step 5: Apply decision gate (in priority order)
    # ------------------------------------------------------------------

    # All claims unknown and no support → no_answer
    if claim_support_rate == 0.0 and contradiction_rate == 0.0:
        return GuardrailedAnswer(
            answer=_NO_ANSWER_STRING,
            decision="no_answer",
            claim_support_rate=0.0,
            contradiction_rate=0.0,
            cited_sources=[],
        )

    # Any contradiction → extractive fallback
    if contradiction_rate > 0:
        return GuardrailedAnswer(
            answer=best_chunk.page_content,
            decision="extractive",
            claim_support_rate=claim_support_rate,
            contradiction_rate=contradiction_rate,
            cited_sources=cited_sources,
        )

    # High support → clean answer
    if claim_support_rate >= SUPPORT_RATE_THRESHOLD:
        return GuardrailedAnswer(
            answer=answer,
            decision="answer",
            claim_support_rate=claim_support_rate,
            contradiction_rate=contradiction_rate,
            cited_sources=cited_sources,
        )

    # Partial support, no contradiction → answer with disclaimer
    return GuardrailedAnswer(
        answer=answer,
        decision="answer_with_disclaimer",
        claim_support_rate=claim_support_rate,
        contradiction_rate=contradiction_rate,
        cited_sources=cited_sources,
    )
