from langchain_core.documents import Document

from src.pipeline.metrics import evaluate_retriever


def test_evaluate_retriever_uses_fixed_precision_denominators():
    results, aggregate = evaluate_retriever(
        retriever_fn=lambda _: [
            Document(page_content="Relevant context", metadata={"source": "a.txt"})
        ],
        eval_set=[{"query": "q", "relevant": ["a.txt"]}],
    )

    assert results[0].precision_at_3 == 1 / 3
    assert results[0].precision_at_6 == 1 / 6
    assert aggregate["precision@3"] == 1 / 3
    assert aggregate["precision@6"] == 1 / 6
