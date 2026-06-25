"""
rag_agent.py — TechStoreRAGAgent: public entry point for the M2 capstone.

This module is the top of the import hierarchy.  All other src/ modules
import from langchain_*, not from this module, to avoid circular imports.

Stop 3 (W6): Implement TechStoreRAGAgent.answer().

Architecture overview:

    User question
        │
        ▼
    TechStoreRAGAgent.answer()
        │
        ├── [always] pipeline/vectorstore → pipeline/reranker   (MMR + cross-encoder)
        │
        ├── [entity-dense] graph/knowledge_graph.query_subgraph  (Graph RAG)
        │
        ├── [numeric/table] multimodal/table_retriever.retrieve  (Table grounding)
        │
        ├── [merge evidence]
        │
        ├── guardrails/writer.build_cited_answer                 (citation binding)
        │
        └── guardrails/verifier.verify_answer                    (decision gate)
                │
                └── GuardrailedAnswer  →  caller

M1 integration (forward reference from Stop 3 Component 4):
    The TechStoreRAGAgent replaces hard-coded product lookups in the M1 MemoryAgent:

        from src.rag_agent import TechStoreRAGAgent

        rag = TechStoreRAGAgent()

        @tool
        def search_knowledge_base(question: str) -> str:
            \"""Search TechStore Plus product manuals, support articles, and policies.\"""
            result = rag.answer(question)
            return result.answer

    This integration works without modifying MemoryAgent because answer() always
    returns a GuardrailedAnswer with a non-empty ``answer`` field (even for no_answer
    decisions, the field contains the safe fallback string).

Forward reference to M3 (LangGraph):
    In Module 3, the manual routing logic inside answer() — the if/else branches
    for entity-dense vs. semantic vs. table queries — will be replaced by a
    LangGraph StateGraph where:
    - Each retrieval path (vector, graph, multimodal) is a ToolNode.
    - The routing logic is an edge condition function.
    - The decision gate is a conditional edge.
    Keeping the components loosely coupled in this module makes that refactor
    straightforward.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GuardrailedAnswer — fully implemented (used by guardrails/verifier.py)
# ---------------------------------------------------------------------------

@dataclass
class GuardrailedAnswer:
    """The return type of :meth:`TechStoreRAGAgent.answer`.

    Carries both the answer text and the guardrail metadata so callers can
    log quality signals, display disclaimers, or route to human escalation.

    Attributes:
        answer: The final answer string to present to the user.
            - For ``decision="answer"`` or ``"answer_with_disclaimer"``: the
              generated answer with inline citations (``[source_filename]``).
            - For ``decision="extractive"``: the verbatim most-relevant chunk.
            - For ``decision="no_answer"``: the exact string
              ``"I don't have that information in our documentation."``.

        decision: One of four values controlling how the answer was produced:
            - ``"answer"`` — claim_support_rate >= 0.85, no contradictions.
            - ``"answer_with_disclaimer"`` — claim_support_rate < 0.85 but
              no contradictions; answer is partially supported.
            - ``"extractive"`` — contradiction_rate > 0; verbatim chunk returned.
            - ``"no_answer"`` — no relevant evidence in the corpus.

        claim_support_rate: Fraction of atomic claims supported by the context.
            Range [0.0, 1.0].  0.0 for no_answer decisions.

        contradiction_rate: Fraction of atomic claims contradicted by the context.
            Range [0.0, 1.0].  0.0 for no_answer decisions.

        cited_sources: Deduplicated list of source identifiers referenced in the
            answer.  Format examples:
            - ``"policy_return_policy.txt"``   (vector store source)
            - ``"[G:Laptop Pro X1->Premium Protection Plan]"`` (graph edge)
            - ``"[TB:laptop_specs.csv:row0]"`` (table row)

    Example::

        result = agent.answer("What is the return period for a refund?")
        assert result.decision in ("answer", "answer_with_disclaimer",
                                   "extractive", "no_answer")
        assert 0.0 <= result.claim_support_rate <= 1.0
        assert isinstance(result.cited_sources, list)
    """

    answer: str
    decision: str  # "answer" | "answer_with_disclaimer" | "extractive" | "no_answer"
    claim_support_rate: float
    contradiction_rate: float
    cited_sources: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        valid_decisions = {
            "answer",
            "answer_with_disclaimer",
            "extractive",
            "ask_clarify",
            "no_answer",
            "refuse",
        }
        if self.decision not in valid_decisions:
            raise ValueError(
                f"decision must be one of {valid_decisions}, got {self.decision!r}"
            )
        if not (0.0 <= self.claim_support_rate <= 1.0):
            raise ValueError(
                f"claim_support_rate must be in [0.0, 1.0], got {self.claim_support_rate}"
            )
        if not (0.0 <= self.contradiction_rate <= 1.0):
            raise ValueError(
                f"contradiction_rate must be in [0.0, 1.0], got {self.contradiction_rate}"
            )


# ---------------------------------------------------------------------------
# Entity / table-query signal keywords
# ---------------------------------------------------------------------------

# Known product model names and warranty tier names from the corpus
_ENTITY_KEYWORDS: frozenset[str] = frozenset({
    "laptop pro x1", "laptop air s2", "laptop lite v3", "workstation z",
    "laptop pro x0", "router nx300", "smart hub home",
    "basic", "standard", "premium", "extended",
    "protection plan", "premium protection plan",
    "standard warranty", "extended warranty",
    "pol-ret", "pol-war", "2023", "2024",
    "warranty tier", "warranty terms",
})

# Signals that an image/visual asset is requested
_IMAGE_KEYWORDS: frozenset[str] = frozenset({
    "image", "photo", "photograph", "picture", "figure", "diagram",
    "show me", "illustration", "slide", "visual", "screenshot",
    "what does", "what do", "looks like", "look like",
})

# Signals that a numeric / CSV lookup is needed
_TABLE_KEYWORDS: frozenset[str] = frozenset({
    "most storage", "most ram", "most memory",
    "how much ram", "how much storage", "how much memory",
    "cheapest", "most expensive", "lowest price", "highest price",
    "storage size", "ram size", "price",
    "compare", "all models", "specifications", "specs",
    "which laptop", "which model",
    "largest storage", "highest ram",
})

_NO_ANSWER_STRING = "I don't have that information in our documentation."


# ---------------------------------------------------------------------------
# TechStoreRAGAgent
# ---------------------------------------------------------------------------

class TechStoreRAGAgent:
    """Production-quality RAG agent for TechStore Plus knowledge queries.

    Integrates four retrieval and generation components:
    1. Vector retrieval: MMR + cross-encoder re-ranking (Stop 2 pipeline).
    2. Graph RAG: entity-aware multi-hop traversal (Stop 3).
    3. Multimodal retrieval: CSV table grounding (Stop 3).
    4. Hallucination guardrails: citation binding + decision gate (Stop 3).

    Usage::

        agent = TechStoreRAGAgent()
        result = agent.answer("What is TechStore Plus's return policy?")
        print(result.answer)
        print(result.decision)         # "answer" | "answer_with_disclaimer" | ...
        print(result.claim_support_rate)

    M1 integration (as a LangChain @tool)::

        from src.rag_agent import TechStoreRAGAgent
        from langchain_core.tools import tool

        rag = TechStoreRAGAgent()

        @tool
        def search_knowledge_base(question: str) -> str:
            \"""Search TechStore Plus product manuals, support articles, and policies.\"""
            result = rag.answer(question)
            return result.answer

    Attributes:
        _vectorstore: Loaded ChromaDB vectorstore instance (initialised lazily).
        _kg:          TechStoreKnowledgeGraph instance (initialised lazily).
        _table_retriever: TableRetriever instance (initialised lazily).

    Note:
        Components are initialised lazily on first call to answer() to avoid
        loading models at import time.  The vectorstore and knowledge graph
        are built once and reused across calls.
    """

    def __init__(self) -> None:
        self._vectorstore = None
        self._kg = None
        self._table_retriever = None
        self._image_retriever = None

    def _ensure_initialized(self) -> None:
        """Lazy-initialise all components on first call to answer().

        1. Vector store: loaded from disk if chroma_db/ exists; otherwise built
           from scratch by loading and chunking data/ documents.
        2. Knowledge graph: always rebuilt from the corpus (in-memory only).
        3. Table retriever: loads CSV files from data/tables/.
        """
        from src.pipeline.loader import load_documents, chunk_documents
        from src.pipeline.vectorstore import build_vectorstore, load_vectorstore
        from src.graph.knowledge_graph import TechStoreKnowledgeGraph
        from src.multimodal.table_retriever import TableRetriever
        from src.multimodal.image_retriever import ImageRetriever

        if self._vectorstore is None:
            chroma_path = Path("./chroma_db")
            if chroma_path.exists() and any(chroma_path.iterdir()):
                self._vectorstore = load_vectorstore()
            else:
                docs = load_documents()
                chunks = chunk_documents(docs)
                self._vectorstore = build_vectorstore(chunks)

        if self._kg is None:
            docs = load_documents()
            self._kg = TechStoreKnowledgeGraph()
            self._kg.extract_and_build(docs)

        if self._table_retriever is None:
            self._table_retriever = TableRetriever()
            self._table_retriever.load_tables()

        if self._image_retriever is None:
            self._image_retriever = ImageRetriever()
            try:
                self._image_retriever.load_images()
            except FileNotFoundError:
                self._image_retriever = None

    def _is_entity_dense(self, question: str) -> bool:
        """Return True if *question* contains entity-dense signals.

        Checks for product model names, warranty tier names, policy version
        references, and named policy documents from the TechStore Plus corpus.

        Entity-dense queries benefit from graph traversal because the knowledge
        graph can surface multi-hop relationships (e.g. Laptop Pro X1 →
        COVERED_BY → Premium Protection Plan → APPLIES_TO → accidental damage)
        that are scattered across multiple documents in the vector store.

        Args:
            question: The user's question string.

        Returns:
            True if the question likely benefits from graph traversal.
        """
        q_lower = question.lower()
        return any(kw in q_lower for kw in _ENTITY_KEYWORDS)

    def _is_image_query(self, question: str) -> bool:
        """Return True if *question* requests a visual asset or diagram.

        Detects keywords like "image", "diagram", "figure", "show me", "looks like"
        that signal the user wants a visual reference rather than (or in addition to)
        a text answer.

        Args:
            question: The user's question string.

        Returns:
            True if the question likely benefits from image retrieval.
        """
        q_lower = question.lower()
        return any(kw in q_lower for kw in _IMAGE_KEYWORDS)

    def _is_table_query(self, question: str) -> bool:
        """Return True if *question* targets numeric or table data.

        Detects superlatives ("most", "cheapest"), explicit comparisons
        ("all models", "compare"), and direct numeric attribute questions
        ("how much RAM", "storage size", "price").

        Table queries route to TableRetriever which performs exact numeric
        lookups on CSV data — more reliable than embedding-based retrieval
        for spec and pricing questions.

        Args:
            question: The user's question string.

        Returns:
            True if the question likely benefits from table retrieval.
        """
        q_lower = question.lower()
        return any(kw in q_lower for kw in _TABLE_KEYWORDS)

    def answer(
        self,
        question: str,
        context: Optional[dict] = None,
    ) -> GuardrailedAnswer:
        """Answer *question* using the full TechStore Plus RAG pipeline.

        Routing logic:
        1. Always: MMR retrieval → cross-encoder re-ranking → top-3 vector docs.
        2. If entity-dense: Graph RAG → query_subgraph → serialised snippets.
        3. If table query: TableRetriever → matching rows → table docs.
        4. Merge all evidence into a single context list.
        5. Citation-binding writer → raw cited answer string.
        6. Claim verifier + decision gate → GuardrailedAnswer.

        The optional *context* dict may contain customer metadata from the M1
        MemoryAgent (e.g., ``{"email": "user@company.com", "recent_intent": "returns"}``).

        Args:
            question: The user's question.
            context:  Optional dict with caller metadata (from M1 MemoryAgent).

        Returns:
            A :class:`GuardrailedAnswer` instance.

        Raises:
            RuntimeError: If initialisation fails (e.g., missing OPENAI_API_KEY).

        Example::

            agent = TechStoreRAGAgent()

            # On-topic query — should return decision="answer"
            r1 = agent.answer("What is the return period for a refund?")
            assert "7" in r1.answer
            assert r1.decision in ("answer", "answer_with_disclaimer")

            # Off-topic query — should return decision="no_answer"
            r2 = agent.answer("What is the capital of France?")
            assert r2.decision == "no_answer"
        """
        from src.pipeline.vectorstore import get_mmr_retriever
        from src.pipeline.reranker import rerank
        from src.guardrails.writer import build_cited_answer
        from src.guardrails.verifier import verify_answer
        from langchain_core.documents import Document

        self._ensure_initialized()

        routing_paths: list[str] = []

        # ------------------------------------------------------------------
        # Step 1+2: MMR retrieval + cross-encoder re-ranking
        # ------------------------------------------------------------------
        retriever = get_mmr_retriever(self._vectorstore)
        mmr_docs = retriever.invoke(question)

        context_docs: list[Document] = []
        if mmr_docs:
            context_docs = rerank(question, mmr_docs)
            routing_paths.append("vector")

        # ------------------------------------------------------------------
        # Step 3: Graph RAG — entity-dense queries
        # ------------------------------------------------------------------
        if self._is_entity_dense(question):
            q_lower = question.lower()
            seed_entities = [kw for kw in _ENTITY_KEYWORDS if kw in q_lower]

            if seed_entities and self._kg.graph.number_of_nodes() > 0:
                try:
                    snippets = self._kg.query_subgraph(seed_entities)
                    for snippet in snippets:
                        content = (
                            f"{snippet['subject']} {snippet['relation']} "
                            f"{snippet['object']}. {snippet['quote']}"
                        ).strip()
                        # Citation format required by Test Case B: [G:subject->object]
                        citation = (
                            f"[G:{snippet['subject']}->{snippet['object']}]"
                        )
                        context_docs.append(Document(
                            page_content=content,
                            metadata={"source": citation},
                        ))
                    if snippets:
                        routing_paths.append("graph")
                except Exception as exc:
                    self._log_optional_route_failure("graph", exc)

        # ------------------------------------------------------------------
        # Step 4: Table retrieval — numeric / comparison queries
        # ------------------------------------------------------------------
        if self._is_table_query(question):
            try:
                table_docs = self._table_retriever.retrieve(question)
                for doc in table_docs:
                    # Promote table_citation into source so the writer cites it
                    citation = doc.metadata.get("table_citation", "")
                    doc.metadata["source"] = citation
                context_docs.extend(table_docs)
                if table_docs:
                    routing_paths.append("table")
            except Exception as exc:
                self._log_optional_route_failure("table", exc)

        # ------------------------------------------------------------------
        # Step 4.5: Image retrieval — visual / diagram queries
        # ------------------------------------------------------------------
        if self._is_image_query(question) and self._image_retriever is not None:
            try:
                image_docs = self._image_retriever.retrieve(question)
                for doc in image_docs:
                    citation = doc.metadata.get("image_citation", "")
                    doc.metadata["source"] = citation
                context_docs.extend(image_docs)
                if image_docs:
                    routing_paths.append("image")
            except Exception as exc:
                self._log_optional_route_failure("image", exc)

        # ------------------------------------------------------------------
        # Step 5: No evidence at all → immediate no_answer
        # ------------------------------------------------------------------
        if not context_docs:
            result = GuardrailedAnswer(
                answer=_NO_ANSWER_STRING,
                decision="no_answer",
                claim_support_rate=0.0,
                contradiction_rate=0.0,
                cited_sources=[],
            )
            self._log_query(question, routing_paths, 0, result)
            return result

        # ------------------------------------------------------------------
        # Step 6: Citation-binding writer
        # ------------------------------------------------------------------
        raw_answer = build_cited_answer(question, context_docs)

        # ------------------------------------------------------------------
        # Step 7: Claim verifier + decision gate
        # ------------------------------------------------------------------
        result = verify_answer(raw_answer, context_docs)
        self._log_query(question, routing_paths, len(context_docs), result)
        return result

    def _log_optional_route_failure(self, route: str, exc: Exception) -> None:
        """Log optional retrieval failures without failing the whole answer."""
        logger.warning("%s retrieval failed: %s", route.capitalize(), exc)
    def _log_query(
        self,
        question: str,
        routing_paths: list[str],
        num_context_docs: int,
        result: "GuardrailedAnswer",
    ) -> None:
        """Emit a structured observability log entry for every answered query."""
        log_entry = {
            "question": question[:120],
            "routing": routing_paths,
            "num_context_docs": num_context_docs,
            "decision": result.decision,
            "claim_support_rate": round(result.claim_support_rate, 3),
            "contradiction_rate": round(result.contradiction_rate, 3),
            "cited_sources": result.cited_sources,
        }
        from src.guardrails.verifier import citation_density, numeric_grounding_rate

        density = citation_density(result.answer)
        grounding = numeric_grounding_rate(result.answer, " ".join(result.cited_sources))
        log_entry["citation_density"] = round(density, 3)
        log_entry["numeric_grounding_rate"] = round(grounding, 3)

        logger.info("[RAG] %s", log_entry)
        print(
            f"[RAG] routing={routing_paths} docs={num_context_docs} "
            f"decision={result.decision} support={result.claim_support_rate:.2f} "
            f"citations={density:.2f}"
        )
