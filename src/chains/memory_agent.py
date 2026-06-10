"""
MemoryAgent — wires HybridMemory and the customer tools into a ReAct agent.

WHY create_react_agent (not AgentExecutor)
───────────────────────────────────────────
AgentExecutor is the legacy way to run tool-using agents in LangChain. It
manages the ReAct loop internally but is not composable with LCEL and is being
deprecated. create_react_agent from langgraph.prebuilt is the current approach:
it exposes the same loop as a LangGraph graph, making it easy to inspect,
extend, and eventually swap for a custom StateGraph in Module 3.

WHY one HybridMemory per customer email
─────────────────────────────────────────
Each customer's conversation is independent. Mixing message histories between
customers would cause the agent to confuse identities, leak personal data, and
produce nonsensical responses. The `memories` dict keyed by email ensures strict
isolation — the same design pattern used in multi-tenant production systems.

This module is part of the completed Week 3 memory-and-tools agent.
"""

from __future__ import annotations

from typing import Protocol

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.components.followup_detector import FollowUpTask, detect_followup_task
from src.components.customer_tools import TOOLS
from src.components.hybrid_memory import HybridMemory
from src.integrations.notion_tasks import NotionConfigError, NotionTaskClient
from src.rag.rag_chain import should_use_rag

MODEL: str = "gpt-4.1-mini"


class TaskClient(Protocol):
    def create_task(self, task: FollowUpTask) -> str:
        ...


class RAGAssistant(Protocol):
    def answer(self, question: str) -> str:
        ...


class MemoryAgent:
    """A memory-aware customer service agent backed by HybridMemory and six tools."""

    def __init__(
        self,
        task_client: TaskClient | None = None,
        rag_assistant: RAGAssistant | None = None,
    ) -> None:
        self._llm = ChatOpenAI(model=MODEL, temperature=0)
        # create_react_agent builds a LangGraph ReAct loop:
        # model call → tool execution (if needed) → model call → final answer
        self._agent = create_react_agent(self._llm, tools=TOOLS)
        # One HybridMemory instance per customer email — never share between customers
        self._memories: dict[str, HybridMemory] = {}
        self._task_client = task_client
        self._rag_assistant = rag_assistant

    # ── Public interface ──────────────────────────────────────────────────────

    def chat(self, customer_email: str, user_text: str) -> str:
        """Process one turn of conversation for a customer and return the reply.

        Args:
            customer_email: Identifies the customer and selects their memory.
            user_text: The message the customer just sent.

        Returns:
            The agent's response as a plain string.
        """
        memory = self._memory_for(customer_email)
        memory.append_user(HumanMessage(content=user_text))

        if self._rag_assistant is not None and should_use_rag(user_text):
            reply_text = self._rag_assistant.answer(user_text)
            memory.append_assistant(AIMessage(content=reply_text))
            return reply_text

        result = self._agent.invoke({"messages": memory.build_messages()})
        reply = result["messages"][-1]
        if not isinstance(reply, AIMessage):
            reply = AIMessage(content=str(reply.content))

        memory.append_assistant(reply)
        reply_text = str(reply.content)
        followup_task = detect_followup_task(customer_email, user_text, reply_text)
        if followup_task is None:
            return reply_text

        task_client = self._task_client
        if task_client is None:
            try:
                task_client = NotionTaskClient.from_env()
            except NotionConfigError:
                return (
                    f"{reply_text}\n\n"
                    "Notion follow-up could not be created because Notion credentials are not configured."
                )

        try:
            task_client.create_task(followup_task)
        except Exception as exc:
            return f"{reply_text}\n\nNotion follow-up could not be created: {exc}"

        return f"{reply_text}\n\nNotion follow-up created."

    def reset(self, customer_email: str) -> None:
        """Clear the conversation history for a specific customer.

        Useful for testing — resets as if the customer is starting fresh.
        """
        self._memories.pop(customer_email, None)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _memory_for(self, email: str) -> HybridMemory:
        """Return the HybridMemory for `email`, creating it on first access."""
        if email not in self._memories:
            self._memories[email] = HybridMemory(customer_email=email)
        return self._memories[email]
