from langchain_core.documents import Document

from src.rag.rag_chain import TechStoreRAGAssistant, should_use_rag


class FakeRetriever:
    def __init__(self, documents):
        self.documents = documents
        self.queries = []

    def similarity_search(self, query, *, k=4):
        self.queries.append((query, k))
        return self.documents


class FakeLLM:
    def __init__(self, content):
        self.content = content
        self.prompts = []

    def invoke(self, messages):
        self.prompts.append(messages)
        content = self.content

        class Response:
            pass

        response = Response()
        response.content = content
        return response


def test_should_use_rag_for_policy_questions():
    assert should_use_rag("What is the return window for laptops?")
    assert should_use_rag("How does smartphone warranty work?")
    assert should_use_rag("Which shipping options are available?")
    assert not should_use_rag("Please remember my email for later")


def test_rag_assistant_answers_with_sources():
    retriever = FakeRetriever(
        [
            Document(
                page_content="Returns are accepted within 30 calendar days.",
                metadata={"title": "techstore_returns.md", "source": "returns.md"},
            )
        ]
    )
    llm = FakeLLM("Customers can return most items within 30 days.")
    assistant = TechStoreRAGAssistant(retriever=retriever, llm=llm)

    answer = assistant.answer("What is the return window?")

    assert "Customers can return most items within 30 days." in answer
    assert "Sources: techstore_returns.md" in answer
    assert retriever.queries == [("What is the return window?", 4)]
    assert "Returns are accepted" in llm.prompts[0][0].content


def test_rag_assistant_returns_not_found_when_no_documents():
    assistant = TechStoreRAGAssistant(retriever=FakeRetriever([]), llm=FakeLLM("unused"))

    answer = assistant.answer("Do you repair espresso machines?")

    assert answer == "I could not find that answer in the TechStore knowledge base."


def test_rag_assistant_accepts_custom_system_prompt():
    retriever = FakeRetriever(
        [
            Document(
                page_content="Use the timeout parameter to avoid hanging forever.",
                metadata={"title": "requests_quickstart.txt"},
            )
        ]
    )
    llm = FakeLLM("Use timeout=5.")
    assistant = TechStoreRAGAssistant(
        retriever=retriever,
        llm=llm,
        system_prompt="You are a Requests documentation assistant.",
        not_found_message="I could not find that answer in the Requests documentation.",
    )

    assistant.answer("How do I set a timeout?")

    assert "Requests documentation assistant" in llm.prompts[0][0].content
