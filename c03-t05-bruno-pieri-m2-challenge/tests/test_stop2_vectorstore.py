from src.pipeline.vectorstore import get_mmr_retriever


class FakeVectorStore:
    def __init__(self):
        self.calls = []

    def as_retriever(self, *, search_type, search_kwargs):
        self.calls.append(
            {"search_type": search_type, "search_kwargs": search_kwargs}
        )
        return "retriever"


def test_get_mmr_retriever_uses_relevance_weighted_mmr():
    vectorstore = FakeVectorStore()

    retriever = get_mmr_retriever(vectorstore)

    assert retriever == "retriever"
    assert vectorstore.calls == [
        {
            "search_type": "mmr",
            "search_kwargs": {"k": 6, "fetch_k": 20, "lambda_mult": 0.85},
        }
    ]
