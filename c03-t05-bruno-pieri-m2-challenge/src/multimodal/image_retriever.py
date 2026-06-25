"""
multimodal/image_retriever.py — Caption-based image retrieval from annotated corpus images.

Position in the architecture:
    data/images/metadata.json  →  ImageRetriever  →  TechStoreRAGAgent (merged evidence)

WHY IMAGE RETRIEVAL?
    Visual assets (product overview slides, setup diagrams, warranty comparison tables)
    carry information that is often absent from prose documents: spatial layout, visual
    emphasis, and side-by-side comparisons. A customer asking "show me the warranty tiers"
    or "what does the Router NX300 setup look like?" is best served by surfacing the
    relevant visual asset alongside text evidence.

    ImageRetriever uses caption-based keyword matching (no VLM API required).
    Each image in data/images/ is described by a human-authored caption and tag list
    stored in metadata.json.  Retrieval scores each image by keyword overlap with
    the user query — the same approach as TableRetriever's Option A.

    Citations use the format [I:filename] so the writer prompt can generate
    correctly tagged inline citations that the verifier can trace back to the
    image metadata entry.

CITATION FORMAT:
    [I:laptop_pro_x1_overview.png] — image filename in data/images/
    Stored in Document metadata as ``image_citation``.
"""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
IMAGES_DIR: Path = Path("data/images")
"""Default directory containing image files and metadata.json."""

IMAGE_RETRIEVAL_K: int = 2
"""Default number of image results to return per query."""

_METADATA_FILE: str = "metadata.json"


class ImageRetriever:
    """Retrieve relevant images as Documents using caption/tag keyword matching.

    Images are indexed via a metadata.json file that stores caption text and
    keyword tags for each image.  Retrieval scores each image by counting
    how many query tokens appear in the combined caption+tags text.

    WHY CAPTION-BASED (not embedding-based)?
        For a small corpus of 3-10 product images, keyword matching on rich
        human-authored captions achieves reliable recall without requiring an
        additional embedding call per image.  The captions are detailed enough
        (model names, feature keywords, technical terms) that cosine distance
        over embeddings would not improve precision meaningfully.

    Attributes:
        _images: List of row Documents, one per image entry in metadata.json.

    Example::

        ir = ImageRetriever()
        ir.load_images(Path("data/images"))
        docs = ir.retrieve("show me the Laptop Pro X1")
        for doc in docs:
            print(doc.page_content[:80], doc.metadata["image_citation"])
    """

    def __init__(self) -> None:
        self._images: list[Document] = []

    def load_images(self, images_dir: Path = IMAGES_DIR) -> None:
        """Parse metadata.json and create one Document per image entry.

        Each Document is created as:
            page_content = caption text (used for keyword scoring)
            metadata = {
                "source":          filename (e.g. "laptop_pro_x1_overview.png"),
                "image_citation":  "[I:filename]",
                "tags":            space-joined tag list,
                "images_dir":      absolute path to the images directory
            }

        Args:
            images_dir: Path to the directory containing metadata.json and PNGs.

        Raises:
            FileNotFoundError: If images_dir or metadata.json does not exist.
            ValueError: If metadata.json is not a valid JSON array.
        """
        images_dir = Path(images_dir)
        if not images_dir.exists():
            raise FileNotFoundError(
                f"Images directory not found: {images_dir}"
            )

        meta_path = images_dir / _METADATA_FILE
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Image metadata file not found: {meta_path}"
            )

        with open(meta_path, encoding="utf-8") as f:
            entries = json.load(f)

        if not isinstance(entries, list):
            raise ValueError(
                f"metadata.json must be a JSON array, got {type(entries).__name__}"
            )

        self._images = []
        for entry in entries:
            filename = entry.get("filename", "unknown.png")
            caption = entry.get("caption", "")
            tags = entry.get("tags", [])

            citation = f"[I:{filename}]"
            tags_str = " ".join(tags)

            doc = Document(
                page_content=caption,
                metadata={
                    "source": filename,
                    "image_citation": citation,
                    "tags": tags_str,
                    "images_dir": str(images_dir.resolve()),
                },
            )
            self._images.append(doc)

        print(f"Loaded {len(self._images)} image(s) from {images_dir}.")

    def retrieve(self, query: str, k: int = IMAGE_RETRIEVAL_K) -> list[Document]:
        """Retrieve the *k* most relevant image Documents for *query*.

        Scores each image by counting how many query tokens appear in the
        combined caption text and tag string (case-insensitive).  Images with
        score > 0 are returned sorted by score descending.  If no images
        score above 0, returns the first *k* images as a fallback.

        The ``image_citation`` metadata field (``[I:filename]``) is
        included so the writer prompt can generate correctly formatted citations.

        Args:
            query: The user's question.
            k:     Maximum number of image Documents to return.

        Returns:
            A list of at most *k* image Documents sorted by relevance descending.

        Raises:
            RuntimeError: If :meth:`load_images` has not been called yet.

        Example::

            docs = ir.retrieve("What does the Router NX300 setup look like?", k=1)
            assert "router_nx300" in docs[0].metadata["image_citation"]
        """
        if not self._images:
            raise RuntimeError(
                "load_images() must be called before retrieve(). "
                "Call ir.load_images() first."
            )

        query_lower = query.lower()
        query_tokens = set(query_lower.split())

        scored: list[tuple[int, Document]] = []
        for doc in self._images:
            combined = (
                doc.page_content.lower()
                + " "
                + doc.metadata.get("tags", "").lower()
            )
            score = sum(1 for token in query_tokens if token in combined)
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = [doc for score, doc in scored if score > 0]
        if not results:
            results = [doc for _, doc in scored]

        return results[:k]
