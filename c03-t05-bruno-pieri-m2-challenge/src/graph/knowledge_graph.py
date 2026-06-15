"""
graph/knowledge_graph.py — Lightweight property graph over the TechStore Plus corpus.

Position in the architecture:
    loader.py  →  knowledge_graph.py  →  TechStoreRAGAgent (query routing)

Stop 3 (W6): Implement TechStoreKnowledgeGraph.

WHY GRAPH RAG?
    Dense vector search finds semantically similar chunks but loses structural
    relationships between entities.  Querying "Which products are covered under
    the extended warranty?" requires knowing:
        Laptop Pro X1  --COVERED_BY-->  Premium Protection Plan
        Router NX300   --COVERED_BY-->  Standard Warranty
        Smart Hub Home --COVERED_BY-->  Premium Protection Plan

    These triples can be extracted from the corpus by an LLM and stored in a
    networkx DiGraph.  Multi-hop traversal (up to 2 hops) then surfaces
    warranty chains, policy amendments, and product-category hierarchies that
    a simple cosine search would miss.

    TechStoreRAGAgent uses graph retrieval when the question contains
    entity-dense signals (product model names, warranty tier names, policy
    version references) and falls back to the vector store for open semantic
    questions.

RELATION ALLOWLIST (to restrict traversal noise):
    COVERED_BY     — product covered by a warranty tier or policy
    PART_OF        — component or accessory belonging to a product family
    AMENDS         — a policy document that supersedes or modifies another
    APPLIES_TO     — a policy or service term that applies to a product category
    REQUIRES       — a product or service that requires another product/service
    SUPERSEDED_BY  — an older policy document replaced by a newer one

Forward reference to M3 (LangGraph):
    In Module 3 you will replace the manual if/else routing inside
    TechStoreRAGAgent.answer() with a LangGraph StateGraph where this graph
    retrieval path is a dedicated ToolNode and the routing decision is an
    edge condition.  Keep the components clean and the interface stable.
"""

from __future__ import annotations

import json
from typing import Optional

import networkx as nx
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_HOPS: int = 2
"""Default number of hops for subgraph traversal.

2 hops is sufficient for most TechStore Plus queries:
    Product → COVERED_BY → WarrantyTier → APPLIES_TO → DamageType
"""

DEFAULT_RELATION_ALLOWLIST: list[str] = [
    "COVERED_BY",
    "PART_OF",
    "AMENDS",
    "APPLIES_TO",
    "REQUIRES",
    "SUPERSEDED_BY",
]
"""Relations that are traversed during subgraph expansion.

A narrow allowlist prevents the traversal from following noisy or
low-confidence triples extracted by the LLM.
"""

_EXTRACTION_MODEL: str = "gpt-4.1-mini"


class TechStoreKnowledgeGraph:
    """In-memory property graph for entity-aware retrieval over TechStore Plus docs.

    The graph is a directed networkx ``DiGraph``.  Nodes represent entities
    (products, policies, services, concepts).  Edges represent typed relations
    with provenance metadata.

    Typical workflow::

        kg = TechStoreKnowledgeGraph()
        kg.extract_and_build(chunks)                       # Stop 3
        snippets = kg.query_subgraph(["Laptop Pro X1"])    # Stop 3

    Attributes:
        graph: The underlying :class:`networkx.DiGraph` instance.

    Note:
        This is an in-memory graph — it is rebuilt on every run.  Persistence
        (serialising to JSON or a graph database) is a known limitation
        documented in the README.
    """

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

    def add_triple(
        self,
        subject: str,
        relation: str,
        obj: str,
        source_id: str,
        quote: str,
        as_of: Optional[str] = None,
    ) -> None:
        """Add a provenance-tracked directed edge to the graph.

        If *subject* or *obj* nodes do not already exist, they are created
        with default attributes.  If the edge already exists, its metadata
        is updated (later triples win on conflicting fields).

        Node attributes set (or updated):
            ``type``  — inferred from ``relation`` or left as ``"Entity"``

        Edge attributes:
            ``relation``  — the relation label (e.g. ``"COVERED_BY"``)
            ``source_id`` — filename of the document this triple came from
            ``quote``     — verbatim short excerpt supporting this triple
            ``as_of``     — optional ISO-8601 date string (e.g. ``"2024-01-01"``)
                            used for temporal policy queries

        Args:
            subject:   Subject entity name (e.g. ``"Laptop Pro X1"``).
            relation:  Relation type from the allowlist (e.g. ``"COVERED_BY"``).
            obj:       Object entity name (e.g. ``"Premium Protection Plan"``).
            source_id: Source document filename (e.g. ``"policy_warranty_terms.txt"``).
            quote:     Short verbatim quote from *source_id* supporting this triple.
            as_of:     Optional date this triple became effective (ISO-8601 string).

        Example::

            kg.add_triple(
                subject="Laptop Pro X1",
                relation="COVERED_BY",
                obj="Premium Protection Plan",
                source_id="policy_warranty_terms.txt",
                quote="Premium Protection Plan covers the Laptop Pro X1 for 36 months",
                as_of="2024-01-01",
            )
        """
        if subject not in self.graph:
            self.graph.add_node(subject, type="Entity")
        if obj not in self.graph:
            self.graph.add_node(obj, type="Entity")

        if self.graph.has_edge(subject, obj):
            self.graph[subject][obj].update({
                "relation": relation,
                "source_id": source_id,
                "quote": quote,
                "as_of": as_of,
            })
        else:
            self.graph.add_edge(
                subject,
                obj,
                relation=relation,
                source_id=source_id,
                quote=quote,
                as_of=as_of,
            )

    def extract_and_build(self, documents: list[Document]) -> None:
        """Extract entity triples from *documents* using an LLM and populate the graph.

        Uses a structured ``ChatOpenAI`` call to decompose each document chunk
        into a list of (subject, relation, object, quote) tuples.

        Only triples whose ``relation`` is in :data:`DEFAULT_RELATION_ALLOWLIST`
        are added to the graph.  Low-confidence or noisy triples are silently
        discarded.

        Args:
            documents: Loaded (and optionally chunked) Document objects.
                       Passing the full un-chunked docs is acceptable here
                       because triple extraction operates at document level.

        Returns:
            None — the graph is mutated in place.

        Raises:
            openai.AuthenticationError: If ``OPENAI_API_KEY`` is missing.

        Example::

            kg = TechStoreKnowledgeGraph()
            kg.extract_and_build(load_documents())
            print(f"Graph has {kg.graph.number_of_nodes()} nodes, "
                  f"{kg.graph.number_of_edges()} edges")
        """
        llm = ChatOpenAI(model=_EXTRACTION_MODEL, temperature=0)
        allowlist_str = ", ".join(DEFAULT_RELATION_ALLOWLIST)
        total_triples = 0

        for doc in documents:
            source_id = doc.metadata.get("source", "unknown")
            # Truncate to avoid token limits on large documents
            text_snippet = doc.page_content[:3000]

            prompt = (
                f"Extract entity relationship triples from the text below.\n"
                f"Return a JSON array of objects, each with these exact keys:\n"
                f"  subject (string), relation (string), object (string), quote (string)\n"
                f"Only use these relation types: {allowlist_str}\n"
                f"The 'quote' field must be a short verbatim excerpt from the text.\n"
                f"Return ONLY a valid JSON array — no markdown, no explanation.\n\n"
                f"Text:\n{text_snippet}"
            )

            try:
                response = llm.invoke([HumanMessage(content=prompt)])
                content = response.content.strip()

                # Strip markdown code fences if the LLM included them
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

                triples = json.loads(content)

                for triple in triples:
                    relation = triple.get("relation", "")
                    if relation not in DEFAULT_RELATION_ALLOWLIST:
                        continue
                    subj = str(triple.get("subject", "")).strip()
                    obj = str(triple.get("object", "")).strip()
                    quote = str(triple.get("quote", "")).strip()
                    if not subj or not obj:
                        continue
                    self.add_triple(
                        subject=subj,
                        relation=relation,
                        obj=obj,
                        source_id=source_id,
                        quote=quote,
                    )
                    total_triples += 1

            except Exception:
                # Skip documents where LLM output cannot be parsed
                continue

        print(
            f"Extracted {total_triples} triples from {len(documents)} documents. "
            f"Graph: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges."
        )

    def query_subgraph(
        self,
        seed_entities: list[str],
        hops: int = DEFAULT_HOPS,
        relation_allowlist: Optional[list[str]] = None,
    ) -> list[dict]:
        """Expand from *seed_entities* and return ranked supporting snippets.

        Starting from each seed entity node, performs a breadth-first traversal
        up to *hops* hops deep.  Only edges whose ``relation`` attribute is in
        *relation_allowlist* are followed.

        Each returned snippet is a dict with the following keys:
            ``subject``   — source entity name
            ``relation``  — edge relation label
            ``object``    — target entity name
            ``source_id`` — provenance document filename
            ``quote``     — verbatim supporting excerpt
            ``as_of``     — effective date string, or None
            ``hop``       — distance from the nearest seed entity (1-indexed)

        Snippets are sorted by ascending ``hop`` (closer = more relevant).
        Duplicate (subject, relation, object) triples are deduplicated.

        Args:
            seed_entities:     Entity names to start traversal from.
                               Case-insensitive match attempted if exact match fails.
            hops:              Maximum traversal depth.  Defaults to :data:`DEFAULT_HOPS`.
            relation_allowlist: Relations to follow.  Defaults to
                               :data:`DEFAULT_RELATION_ALLOWLIST`.

        Returns:
            A list of snippet dicts, sorted by hop distance ascending.

        Raises:
            ValueError: If the graph has not been populated (no nodes).

        Example::

            snippets = kg.query_subgraph(["Laptop Pro X1"], hops=2)
            for s in snippets:
                print(f"{s['subject']} --{s['relation']}--> {s['object']} "
                      f"[{s['source_id']}]")
        """
        if self.graph.number_of_nodes() == 0:
            raise ValueError(
                "Knowledge graph is empty. Call extract_and_build() first."
            )

        if relation_allowlist is None:
            relation_allowlist = DEFAULT_RELATION_ALLOWLIST

        # Build a case-insensitive lookup map for fuzzy seed matching
        node_map: dict[str, str] = {n.lower(): n for n in self.graph.nodes()}

        # Resolve seed entities (exact then case-insensitive)
        resolved_seeds: list[str] = []
        for seed in seed_entities:
            if seed in self.graph:
                resolved_seeds.append(seed)
            elif seed.lower() in node_map:
                resolved_seeds.append(node_map[seed.lower()])

        snippets: list[dict] = []
        seen: set[tuple] = set()

        for seed in resolved_seeds:
            # BFS up to `hops` depth
            queue: list[tuple[str, int]] = [(seed, 0)]
            visited: set[str] = {seed}

            while queue:
                node, depth = queue.pop(0)
                if depth >= hops:
                    continue

                for _, neighbor, data in self.graph.out_edges(node, data=True):
                    relation = data.get("relation", "")
                    if relation not in relation_allowlist:
                        continue

                    triple_key = (node, relation, neighbor)
                    if triple_key not in seen:
                        seen.add(triple_key)
                        snippets.append({
                            "subject": node,
                            "relation": relation,
                            "object": neighbor,
                            "source_id": data.get("source_id", ""),
                            "quote": data.get("quote", ""),
                            "as_of": data.get("as_of"),
                            "hop": depth + 1,
                        })

                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, depth + 1))

        snippets.sort(key=lambda x: x["hop"])
        return snippets
