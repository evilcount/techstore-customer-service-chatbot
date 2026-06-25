from pathlib import Path

import pytest

from src.multimodal.image_retriever import ImageRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = PROJECT_ROOT / "data" / "images"


def test_image_retriever_returns_router_setup_diagram():
    retriever = ImageRetriever()
    retriever.load_images(IMAGES_DIR)

    docs = retriever.retrieve("What does the Router NX300 setup diagram show?", k=1)

    assert len(docs) == 1
    assert docs[0].metadata["image_citation"] == "[I:router_nx300_setup_diagram.png]"
    assert "router" in docs[0].page_content.lower()


def test_image_retriever_requires_loading_before_retrieval():
    retriever = ImageRetriever()

    with pytest.raises(RuntimeError, match="load_images"):
        retriever.retrieve("router setup")
