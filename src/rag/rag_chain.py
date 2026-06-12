from __future__ import annotations

from typing import Protocol

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


class Retriever(Protocol):
    def similarity_search(self, query: str, *, k: int = 4) -> list[Document]:
        ...


class LLM(Protocol):
    def invoke(self, messages: list[HumanMessage]):
        ...


class TechStoreRAGAssistant:
    def __init__(
        self,
        *,
        retriever: Retriever,
        llm: LLM | None = None,
        k: int = 4,
        system_prompt: str = "You are TechStore Plus support.",
        not_found_message: str = "I could not find that answer in the TechStore knowledge base.",
    ) -> None:
        self._retriever = retriever
        self._llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self._k = k
        self._system_prompt = system_prompt
        self._not_found_message = not_found_message

    def answer(self, question: str) -> str:
        documents = self._retriever.similarity_search(question, k=self._k)
        if not documents:
            return self._not_found_message

        context = _format_context(documents)
        prompt = (
            f"{self._system_prompt} Answer the question using only the context below. "
            f"If the context does not contain the answer, say: {self._not_found_message}\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}"
        )
        response = self._llm.invoke([HumanMessage(content=prompt)])
        answer_text = str(response.content).strip()
        sources = _format_sources(documents)
        return f"{answer_text}\n\nSources: {sources}"


def _format_context(documents: list[Document]) -> str:
    parts = []
    for index, document in enumerate(documents, start=1):
        title = document.metadata.get("title") or document.metadata.get("source", "Unknown source")
        parts.append(f"[{index}] {title}\n{document.page_content}")
    return "\n\n".join(parts)


def _format_sources(documents: list[Document]) -> str:
    sources = []
    for document in documents:
        source = document.metadata.get("title") or document.metadata.get("source", "Unknown source")
        if source not in sources:
            sources.append(str(source))
    return ", ".join(sources)
