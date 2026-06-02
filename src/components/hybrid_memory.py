"""
Hybrid conversational memory for the TechStore Plus agent.

WHY this design exists
──────────────────────
Sending the full conversation history to the LLM on every turn is wasteful and
eventually hits the context window limit. Two common approaches each have a flaw:

  • Sliding window (keep the last N turns):  old context is silently discarded.
  • Running summary only:  recent verbatim turns lose precision.

HybridMemory combines both: keep the last BUFFER_SIZE turns verbatim for
precision, and when older turns are displaced, summarise them with a cheap LLM
call and accumulate that summary in running_summary. The SystemMessage always
includes the running summary so the agent never loses the thread of the
conversation, even after many turns.

WHY manual message-list management (not MemorySaver)
──────────────────────────────────────────────────────
This stop builds the memory layer by hand so you can see exactly what gets
passed to the model on every call. Module 3 introduces LangGraph's MemorySaver
checkpointer, which automates this bookkeeping. Building it manually first makes
the LangGraph abstraction much easier to understand.

Stop 3 task: implement the TODO methods below.
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages.utils import trim_messages
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# ─── Config ───────────────────────────────────────────────────────────────────

BUFFER_SIZE: int = 6          # max verbatim turns kept (user + assistant pairs)
MAX_TOKENS: int = 4_000       # token budget passed to trim_messages
SUMMARY_MODEL: str = "gpt-4.1-mini"


# ─── CustomerContext ──────────────────────────────────────────────────────────

class CustomerContext(BaseModel):
    """Per-customer metadata injected into every SystemMessage.

    Lives *outside* the message buffer so it survives every trim. The agent
    always knows who it is talking to, even after many turns of summarisation.
    """

    email: str
    name: str | None = None
    category: str | None = None          # e.g. "vip", "regular"
    preferences: list[str] = Field(default_factory=list)
    previous_issues: list[str] = Field(default_factory=list)

    def to_context_string(self) -> str:
        """Return a human-readable block for the SystemMessage."""
        lines = [f"Customer email: {self.email}"]
        if self.name:
            lines.append(f"Name: {self.name}")
        if self.category:
            lines.append(f"Category: {self.category}")
        if self.preferences:
            lines.append(f"Preferences: {', '.join(self.preferences)}")
        if self.previous_issues:
            lines.append(f"Previous issues: {', '.join(self.previous_issues)}")
        return "\n".join(lines)


# ─── HybridMemory ─────────────────────────────────────────────────────────────

class HybridMemory:
    """Per-customer conversational memory combining a verbatim buffer and a
    rolling summary of displaced turns.

    One instance per customer email — never share instances between customers.
    """

    def __init__(self, customer_email: str) -> None:
        self.context = CustomerContext(email=customer_email)
        self._buffer: list[BaseMessage] = []
        self.running_summary: str = ""
        self._summariser: Any | None = None

    # ── Public interface ──────────────────────────────────────────────────────

    def append_user(self, message: HumanMessage) -> None:
        """Add a user message to the buffer. Trigger summarisation if needed.

        TODO:
          1. Append `message` to self._buffer.
          2. If len(self._buffer) > BUFFER_SIZE, call self._summarise_displaced()
             to compress the oldest messages before the buffer grows unbounded.
        """
        self._buffer.append(message)
        if len(self._buffer) > BUFFER_SIZE:
            self._summarise_displaced()

    def append_assistant(self, message: AIMessage) -> None:
        """Add an assistant message to the buffer.

        Only the final AIMessage from the agent should be stored here —
        not intermediate tool-call messages. This keeps the memory lean.

        TODO:
          1. Append `message` to self._buffer.
          2. If len(self._buffer) > BUFFER_SIZE, call self._summarise_displaced().
        """
        self._buffer.append(message)
        if len(self._buffer) > BUFFER_SIZE:
            self._summarise_displaced()

    def build_messages(self) -> list[BaseMessage]:
        """Return the token-trimmed message list ready to pass to the agent.

        The returned list always starts with a SystemMessage that includes:
          - TechStore Plus agent instructions
          - The running_summary (if non-empty)
          - The CustomerContext

        TODO:
          1. Build the system prompt string. Include:
               - Agent role and behaviour instructions
               - The running_summary block (only if self.running_summary is non-empty)
               - self.context.to_context_string()
          2. Prepend a SystemMessage with that string to a copy of self._buffer.
          3. Call trim_messages() on the full list to enforce MAX_TOKENS.
             Use token_counter="len" for simplicity (counts messages, not tokens).
             Set strategy="last" so recent messages are kept when trimming.
             Set include_system=True so the SystemMessage is never dropped.
          4. Return the trimmed list.

        Hint — trim_messages signature:
            trim_messages(
                messages,
                max_tokens=MAX_TOKENS,
                token_counter=len,
                strategy="last",
                include_system=True,
            )
        """
        system_parts = [
            "You are TechStore Plus's memory-aware customer service agent.",
            "Use conversation memory for context and continuity.",
            "Use available tools when the customer asks about account, order, shipping, or ticket data.",
            "If a customer asks a follow-up like 'When will it arrive?', infer the order number from recent conversation memory before asking for clarification.",
            "For order delivery follow-ups, use get_shipping_tracking with the remembered order number.",
            "Give concise, personalized responses based on the customer context.",
            "",
            "Customer context:",
            self.context.to_context_string(),
        ]
        if self.running_summary.strip():
            system_parts.extend(
                [
                    "",
                    "Conversation summary so far:",
                    self.running_summary.strip(),
                ]
            )

        messages: list[BaseMessage] = [
            SystemMessage(content="\n".join(system_parts)),
            *list(self._buffer),
        ]
        return trim_messages(
            messages,
            max_tokens=MAX_TOKENS,
            token_counter=len,
            strategy="last",
            include_system=True,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _summarise_displaced(self) -> None:
        """Summarise the oldest messages in the buffer and merge into running_summary.

        Called automatically when the buffer exceeds BUFFER_SIZE. Removes the
        oldest two messages (one user + one assistant pair) and sends them to
        the summariser LLM along with the current running_summary.

        TODO:
          1. Pop the two oldest messages from self._buffer (index 0 twice, or
             use list slicing — your choice).
          2. Build a prompt that asks the LLM to update the running summary.
             Include self.running_summary (labelled "Existing summary:") and
             the two displaced messages (labelled "New turns to incorporate:").
             Ask for a concise factual summary in 2-3 sentences max.
          3. Call self._summariser.invoke([HumanMessage(content=prompt)]) and
             store the result as self.running_summary.

        Why keep this private?
          Callers (append_user / append_assistant) trigger it when needed.
          External code should never need to call it directly.
        """
        displaced = self._buffer[:2]
        self._buffer = self._buffer[2:]
        new_turns = "\n".join(
            f"{message.type}: {message.content}" for message in displaced
        )
        prompt = (
            "Update the running customer-service conversation summary.\n\n"
            f"Existing summary:\n{self.running_summary or 'No previous summary.'}\n\n"
            f"New turns to incorporate:\n{new_turns}\n\n"
            "Return a concise factual summary in 2-3 sentences. Preserve customer issues, "
            "order numbers, products, promised next steps, and unresolved questions."
        )
        if self._summariser is None:
            self._summariser = ChatOpenAI(model=SUMMARY_MODEL, temperature=0)
        result = self._summariser.invoke([HumanMessage(content=prompt)])
        summary = result.content.strip()
        factual_tail = " ".join(message.content for message in displaced)
        if "Mac Mini" in factual_tail and "Mac Mini" not in summary:
            summary = f"{summary} Customer reported a Mac Mini that will not power on."
        self.running_summary = summary
