"""
Week 7 — LangGraph Challenge: a hand-rolled StateGraph math agent.

WHY a custom StateGraph (not create_react_agent)
─────────────────────────────────────────────────
src.chains.memory_agent uses langgraph.prebuilt.create_react_agent, which
hides the agent/tool loop behind a single call. Its module docstring frames
that as a stepping stone "eventually swap for a custom StateGraph in
Module 3" — this module is that swap: typed state with reducers, an
explicit loop-cap guard, and checkpointing are all visible and testable
instead of buried inside the prebuilt loop.

WHY loosely-typed tool arguments (str | float | int)
──────────────────────────────────────────────────────
LangChain auto-generates a Pydantic schema from a @tool function's type
hints. If `a`/`b` were typed as `float`, a bad value like "abc" would be
rejected by that generated schema *before* the tool body ever runs, and
the resulting error message would be framework-authored rather than ours.
src.components.customer_tools establishes this repo's convention that
tools never raise — they always return a human-readable string so the
agent can continue the conversation. Loosening the parameter types lets
the tool body itself validate and produce that friendly string.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

MODEL: str = "gpt-4o-mini"
MAX_TOOL_CALLS: int = 5


class AgentState(TypedDict):
    """Minimal state: message history plus small counters/ids, not large payloads."""

    messages: Annotated[list[BaseMessage], add_messages]
    tool_calls: Annotated[int, operator.add]
    retries: Annotated[int, operator.add]
    errors: Annotated[list[str], operator.add]


# ─── Tools ──────────────────────────────────────────────────────────────────
# Error strings use a machine-parseable "ERROR:<CLASS>: <detail>" sentinel so
# agent_node can turn them into structured `errors` state entries below,
# without the tool itself ever raising. CLASS is one of VALIDATION (fatal,
# never retried) or TRANSIENT (would be retried under the policy described in
# the Week 7 notebook write-up).


def _parse_number(value: str | float | int) -> tuple[float | None, str | None]:
    try:
        return float(value), None
    except (TypeError, ValueError):
        return None, f"could not parse {value!r} as a number"


@tool
def add(a: str | float | int, b: str | float | int) -> str:
    """Add two numbers and return their sum.

    Args:
        a: The first addend (a number, e.g. 2.5, or a numeric string, e.g. "2.5").
        b: The second addend (a number, e.g. 7, or a numeric string, e.g. "7").
    """
    parsed_a, error_a = _parse_number(a)
    if error_a:
        return f"ERROR:VALIDATION: invalid value for a - {error_a}"
    parsed_b, error_b = _parse_number(b)
    if error_b:
        return f"ERROR:VALIDATION: invalid value for b - {error_b}"
    return str(parsed_a + parsed_b)


@tool
def multiply(a: str | float | int, b: str | float | int) -> str:
    """Multiply two numbers and return their product.

    Args:
        a: The first factor (a number, e.g. 2.5, or a numeric string, e.g. "2.5").
        b: The second factor (a number, e.g. 7, or a numeric string, e.g. "7").
    """
    parsed_a, error_a = _parse_number(a)
    if error_a:
        return f"ERROR:VALIDATION: invalid value for a - {error_a}"
    parsed_b, error_b = _parse_number(b)
    if error_b:
        return f"ERROR:VALIDATION: invalid value for b - {error_b}"
    return str(parsed_a * parsed_b)


TOOLS = [add, multiply]


# ─── Nodes ──────────────────────────────────────────────────────────────────


def make_agent_node(llm):
    """Build the agent node bound to a specific LLM (real or fake, for tests)."""

    def agent_node(state: AgentState) -> dict:
        # Any ToolMessages the previous "tools" node just produced are the
        # trailing contiguous block of state["messages"] — the only edge
        # into "agent" besides START is tools -> agent, so this is safe.
        new_errors: list[str] = []
        transient_count = 0
        for msg in reversed(state["messages"]):
            if not isinstance(msg, ToolMessage):
                break
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            if content.startswith("ERROR:"):
                _, cls, detail = content.split(":", 2)
                cls = cls.strip()
                new_errors.append(f"tool={msg.name} class={cls} detail={detail.strip()[:160]}")
                if cls == "TRANSIENT":
                    transient_count += 1

        response = llm.invoke(state["messages"])
        requested = len(getattr(response, "tool_calls", None) or [])
        return {
            "messages": [response],
            "tool_calls": requested,
            "errors": new_errors,
            "retries": transient_count,
        }

    return agent_node


def route_after_agent(state: AgentState) -> str:
    """Decide the next node after "agent": tools_condition, gated by the loop cap.

    Only a conditional edge can choose the next node in LangGraph — node
    functions just return state deltas — so the loop-cap check lives here,
    not inside agent_node or tools_condition itself. The `tool_calls`
    counter is incremented in agent_node before this function runs (LangGraph
    applies a node's state delta before evaluating its outgoing conditional
    edge), so an over-limit request is routed to safe_exit and abandoned
    before it ever executes.
    """
    base_route = tools_condition(state)
    if base_route != "tools":
        return END
    if state["tool_calls"] >= MAX_TOOL_CALLS:
        return "safe_exit"
    return "tools"


def safe_exit_node(state: AgentState) -> dict:
    message = AIMessage(
        content=(
            f"I've hit the tool-call safety limit ({MAX_TOOL_CALLS}) for this turn. "
            "To keep things reliable, I'm stopping here rather than looping indefinitely. "
            "Please rephrase your request more specifically, or ask me to continue."
        )
    )
    return {
        "messages": [message],
        "errors": [f"guard=loop_cap tool_calls={state['tool_calls']} limit={MAX_TOOL_CALLS}"],
    }


# ─── Graph factory ──────────────────────────────────────────────────────────


def build_graph(llm=None, checkpointer=None, interrupt_before: list[str] | None = None):
    """Compile the Week 7 agent graph.

    Args:
        llm: Tool-bound chat model to drive the agent node. Defaults to a
            real ChatOpenAI(model=MODEL, temperature=0).bind_tools(TOOLS).
            Tests inject a fake double here instead.
        checkpointer: Defaults to a fresh InMemorySaver().
        interrupt_before: Passed straight through to .compile(); used to
            pause a run before a given node (e.g. ["tools"]) to demonstrate
            replay/resume.
    """
    if llm is None:
        llm = ChatOpenAI(model=MODEL, temperature=0).bind_tools(TOOLS)
    if checkpointer is None:
        checkpointer = InMemorySaver()

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", make_agent_node(llm))
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.add_node("safe_exit", safe_exit_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        route_after_agent,
        {"tools": "tools", "safe_exit": "safe_exit", END: END},
    )
    workflow.add_edge("tools", "agent")
    workflow.add_edge("safe_exit", END)

    return workflow.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)


def initial_state(query: str) -> AgentState:
    return {
        "messages": [HumanMessage(content=query)],
        "tool_calls": 0,
        "retries": 0,
        "errors": [],
    }
