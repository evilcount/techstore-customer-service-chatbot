import uuid

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from src.chains.langgraph_challenge_agent import (
    MAX_TOOL_CALLS,
    build_graph,
    initial_state,
    multiply,
)


class FakeToolCallingLLM:
    """Hand-rolled fake LLM double — no live API calls, mirrors
    tests/test_memory_agent_rag_unit.py's FakeGraphAgent style."""

    def __init__(self, responses: list[AIMessage]):
        self._responses = list(responses)
        self.calls: list[list] = []

    def invoke(self, messages):
        self.calls.append(messages)
        return self._responses.pop(0)


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _tool_call_message(name: str, args: dict, call_id: str | None = None) -> AIMessage:
    call_id = call_id or f"call_{uuid.uuid4().hex[:8]}"
    return AIMessage(
        content="",
        tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"}],
    )


def test_math_chain_uses_both_tools_and_returns_28_5():
    # NOTE: the challenge spec's worked example ("Add 2.5 and 7, then multiply
    # by 3" -> 27.0) is arithmetically inconsistent: (2.5 + 7) * 3 = 28.5, not
    # 27.0. This test asserts the mathematically correct result instead of
    # the spec's literal (wrong) number — see the notebook write-up for the
    # same note.
    fake_llm = FakeToolCallingLLM(
        [
            _tool_call_message("add", {"a": 2.5, "b": 7}),
            _tool_call_message("multiply", {"a": 9.5, "b": 3}),
            AIMessage(content="2.5 + 7 = 9.5, then 9.5 * 3 = 28.5."),
        ]
    )
    app = build_graph(llm=fake_llm, checkpointer=InMemorySaver())

    result = app.invoke(
        initial_state("Add 2.5 and 7, then multiply by 3."),
        config=_config("test-math-chain"),
    )

    final_message = result["messages"][-1]
    assert "28.5" in final_message.content
    assert result["tool_calls"] == 2
    assert result["errors"] == []
    assert len(fake_llm.calls) == 3


def test_loop_cap_exits_via_safe_exit_at_exactly_five():
    # Always proposes another tool call — never a plain-text final answer.
    responses = [_tool_call_message("add", {"a": 1, "b": 1}) for _ in range(MAX_TOOL_CALLS + 2)]
    fake_llm = FakeToolCallingLLM(responses)
    app = build_graph(llm=fake_llm, checkpointer=InMemorySaver())

    result = app.invoke(initial_state("keep refining the number; try again and again"), config=_config("test-loop-cap"))

    assert result["tool_calls"] == MAX_TOOL_CALLS
    final_message = result["messages"][-1]
    assert "safety limit" in final_message.content
    assert any(entry.startswith("guard=loop_cap") for entry in result["errors"])
    # The agent node runs once per accepted tool call; the call that would
    # push the cumulative count to MAX_TOOL_CALLS is the one route_after_agent
    # rejects (routes to safe_exit instead of tools), so it's never executed.
    assert len(fake_llm.calls) == MAX_TOOL_CALLS


def test_invalid_input_rejected_with_friendly_validation_error():
    result = multiply.invoke({"a": "abc", "b": 5})

    assert result.startswith("ERROR:VALIDATION")
    assert "abc" in result


def test_replay_resumes_a_partially_completed_run_via_same_thread_id():
    fake_llm = FakeToolCallingLLM(
        [
            _tool_call_message("add", {"a": 2, "b": 2}, call_id="call_abc123"),
            AIMessage(content="2 + 2 = 4."),
        ]
    )
    checkpointer = InMemorySaver()
    app = build_graph(llm=fake_llm, checkpointer=checkpointer, interrupt_before=["tools"])
    config = _config("test-replay")

    app.invoke(initial_state("Add 2 and 2."), config=config)
    state_before_resume = app.get_state(config)
    assert state_before_resume.next == ("tools",)

    pending_call_id = state_before_resume.values["messages"][-1].tool_calls[0]["id"]

    result = app.invoke(None, config=config)

    tool_message = next(m for m in result["messages"] if getattr(m, "tool_call_id", None) == pending_call_id)
    assert tool_message.content == "4.0"
    assert result["messages"][-1].content == "2 + 2 = 4."
    assert app.get_state(config).next == ()
