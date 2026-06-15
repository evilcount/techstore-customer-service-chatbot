"""
multimodal/table_retriever.py — Table-grounded retrieval from CSV files.

Position in the architecture:
    data/tables/*.csv  →  TableRetriever  →  TechStoreRAGAgent (merged evidence)

Stop 3 (W6): Implement TableRetriever.

WHY TABLE RETRIEVAL (for your docstring)?
    Numeric and comparison queries ("Which laptop has the most storage?",
    "How much does the Laptop Pro X1 cost?") require exact cell values.
    A prose embedding retriever may rank a paragraph that mentions 512 GB
    in context lower than a paragraph about storage best practices.

    TableRetriever converts each CSV row into a LangChain Document:
    - page_content: a natural-language serialisation of the row
      (e.g. "model=Laptop Pro X1, ram_gb=16, storage_gb=512, price_usd=1299,
              warranty_tier=premium")
    - metadata: row_index, column_names, source_file, table_citation

    Retrieval uses Option A (keyword/column matching) for general queries and
    Option C (numeric sort) for superlative queries.  Both methods return
    Documents with [TB:filename:rowN] citations so the writer prompt can
    cite them correctly.

CITATION FORMAT:
    [TB:laptop_specs.csv:row2] — means row index 2 of laptop_specs.csv
    Include this citation in the Document's metadata as ``table_citation``.
"""

from __future__ import annotations

import csv
from pathlib import Path

from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TABLES_DIR: Path = Path("data/tables")
"""Default directory containing CSV table files."""

TABLE_RETRIEVAL_K: int = 3
"""Default number of table rows to return per query."""

# Superlative patterns mapped to (column_name, sort_ascending)
# sort_ascending=True  → lowest value wins (cheapest, smallest)
# sort_ascending=False → highest value wins (most, largest, most expensive)
_SUPERLATIVE_PATTERNS: list[tuple[str, str, bool]] = [
    ("most storage", "storage_gb", False),
    ("largest storage", "storage_gb", False),
    ("highest storage", "storage_gb", False),
    ("most ram", "ram_gb", False),
    ("highest ram", "ram_gb", False),
    ("most memory", "ram_gb", False),
    ("cheapest", "price_usd", True),
    ("lowest price", "price_usd", True),
    ("least expensive", "price_usd", True),
    ("most expensive", "price_usd", False),
    ("highest price", "price_usd", False),
]


class TableRetriever:
    """Parse CSV tables and retrieve relevant rows as Documents.

    Tables are loaded once via :meth:`load_tables` and cached in memory as
    lists of row Documents.  :meth:`retrieve` then finds the most relevant
    rows for a given query using keyword matching (Option A) or numeric
    sorting for superlative queries (Option C).

    WHY TABLE RETRIEVAL?
        Prose embedding retrievers compress numeric values into continuous
        vector space and cannot guarantee exact cell value recall.  A query
        such as "How much RAM does the Laptop Pro X1 have?" requires exact
        lookup of ``ram_gb=16`` from ``laptop_specs.csv``.  Converting each
        CSV row to a natural-language string and retrieving by keyword/numeric
        comparison provides reliable, hallucination-free grounding for
        specification queries.

    Attributes:
        _tables: Dict mapping filename → list of row Documents.

    Example::

        tr = TableRetriever()
        tr.load_tables(Path("data/tables"))
        docs = tr.retrieve("How much RAM does the Laptop Pro X1 have?")
        for doc in docs:
            print(doc.page_content, doc.metadata["table_citation"])
    """

    def __init__(self) -> None:
        self._tables: dict[str, list[Document]] = {}

    def load_tables(self, tables_dir: Path = TABLES_DIR) -> None:
        """Parse all CSV files in *tables_dir* into row-level Documents.

        For each CSV file:
        - Read all rows using the ``csv`` standard library.
        - Serialise each row as a natural-language string:
              "model=Laptop Pro X1, ram_gb=16, storage_gb=512, price_usd=1299,
               warranty_tier=premium"
        - Create a Document with:
              page_content = the serialised row string
              metadata = {
                  "source":          filename (e.g. "laptop_specs.csv"),
                  "row_index":       row number (0-indexed, excluding header),
                  "column_names":    comma-separated column names string,
                  "table_citation":  "[TB:filename:rowN]"
              }

        After loading, print a summary: "Loaded N rows from M tables."

        Args:
            tables_dir: Path to the directory containing CSV files.

        Raises:
            FileNotFoundError: If *tables_dir* does not exist.
            ValueError: If a CSV file has no header row.
        """
        tables_dir = Path(tables_dir)
        if not tables_dir.exists():
            raise FileNotFoundError(
                f"Tables directory not found: {tables_dir}"
            )

        total_rows = 0

        for csv_path in sorted(tables_dir.glob("*.csv")):
            filename = csv_path.name
            rows: list[Document] = []

            with open(csv_path, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    raise ValueError(f"CSV file has no header row: {csv_path}")

                column_names = ", ".join(reader.fieldnames)

                for i, row in enumerate(reader):
                    content = ", ".join(
                        f"{key}={value}" for key, value in row.items()
                    )
                    citation = f"[TB:{filename}:row{i}]"
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": filename,
                            "row_index": i,
                            "column_names": column_names,
                            "table_citation": citation,
                        },
                    )
                    rows.append(doc)

            self._tables[filename] = rows
            total_rows += len(rows)

        print(f"Loaded {total_rows} rows from {len(self._tables)} tables.")

    def retrieve(self, query: str, k: int = TABLE_RETRIEVAL_K) -> list[Document]:
        """Retrieve the *k* most relevant table rows for *query*.

        Implements two complementary strategies:

        **Option C — Numeric comparison (superlative queries):**
            Detects superlative patterns ("most storage", "cheapest", etc.) and
            sorts the relevant numeric column, returning the top/bottom row.
            This provides exact numeric grounding for comparison questions.

        **Option A — Keyword matching (general queries):**
            Tokenises the query and scores each row by the number of matching
            tokens found in row content or column names (case-insensitive).
            Ties are broken by row index.

        The ``table_citation`` metadata field (``[TB:filename:rowN]``) is
        included so the writer prompt can generate correctly formatted citations.

        Args:
            query: The user's question (e.g. "Which laptop has the most storage?").
            k:     Maximum number of row Documents to return.

        Returns:
            A list of at most *k* row Documents sorted by relevance descending.

        Raises:
            RuntimeError: If :meth:`load_tables` has not been called yet.

        Example::

            docs = tr.retrieve("How much does the Laptop Lite V3 cost?", k=1)
            assert "499" in docs[0].page_content
            assert "[TB:laptop_specs.csv:" in docs[0].metadata["table_citation"]
        """
        if not self._tables:
            raise RuntimeError(
                "load_tables() must be called before retrieve(). "
                "Call tr.load_tables() first."
            )

        query_lower = query.lower()

        # Option C: superlative / numeric sort
        for phrase, column, ascending in _SUPERLATIVE_PATTERNS:
            if phrase in query_lower:
                return self._sort_by_column(column, ascending, k)

        # Option A: keyword matching across all tables
        return self._keyword_match(query_lower, k)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sort_by_column(
        self, column: str, ascending: bool, k: int
    ) -> list[Document]:
        """Return rows sorted by *column* numerically."""
        all_rows: list[Document] = []
        for rows in self._tables.values():
            all_rows.extend(rows)

        sortable: list[tuple[float, Document]] = []
        for doc in all_rows:
            row_dict = _parse_row_content(doc.page_content)
            try:
                val = float(row_dict.get(column, "0") or "0")
                sortable.append((val, doc))
            except ValueError:
                pass

        sortable.sort(key=lambda x: x[0], reverse=not ascending)
        return [doc for _, doc in sortable[:k]]

    def _keyword_match(self, query_lower: str, k: int) -> list[Document]:
        """Score all rows by keyword overlap with *query_lower*."""
        query_tokens = set(query_lower.split())

        all_docs: list[Document] = []
        for rows in self._tables.values():
            all_docs.extend(rows)

        scored: list[tuple[int, Document]] = []
        for doc in all_docs:
            content_lower = doc.page_content.lower()
            col_lower = doc.metadata.get("column_names", "").lower()
            score = sum(
                1 for token in query_tokens
                if token in content_lower or token in col_lower
            )
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:k]]


def _parse_row_content(content: str) -> dict[str, str]:
    """Parse a serialised row string back into a key→value dict."""
    result: dict[str, str] = {}
    for pair in content.split(", "):
        if "=" in pair:
            key, _, value = pair.partition("=")
            result[key.strip()] = value.strip()
    return result
