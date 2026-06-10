from langchain_core.messages import AIMessage

from src.chains.memory_agent import MemoryAgent


class FakeGraphAgent:
    def __init__(self):
        self.calls = []

    def invoke(self, payload):
        self.calls.append(payload)
        return {"messages": [*payload["messages"], AIMessage(content="Fallback answer.")]}


class FakeRAGAssistant:
    def __init__(self):
        self.questions = []

    def answer(self, question):
        self.questions.append(question)
        return "RAG answer.\n\nSources: techstore_returns.md"


def build_agent(monkeypatch, rag_assistant=None):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    agent = MemoryAgent(rag_assistant=rag_assistant)
    agent._agent = FakeGraphAgent()
    return agent


def test_chat_uses_rag_for_policy_question(monkeypatch):
    rag_assistant = FakeRAGAssistant()
    agent = build_agent(monkeypatch, rag_assistant=rag_assistant)

    reply = agent.chat("customer@example.com", "What is the return window for laptops?")

    assert reply == "RAG answer.\n\nSources: techstore_returns.md"
    assert rag_assistant.questions == ["What is the return window for laptops?"]
    assert agent._agent.calls == []


def test_chat_falls_back_to_existing_agent_for_non_rag_question(monkeypatch):
    rag_assistant = FakeRAGAssistant()
    agent = build_agent(monkeypatch, rag_assistant=rag_assistant)

    reply = agent.chat("customer@example.com", "Please remember that I prefer email.")

    assert reply == "Fallback answer."
    assert rag_assistant.questions == []
    assert len(agent._agent.calls) == 1
