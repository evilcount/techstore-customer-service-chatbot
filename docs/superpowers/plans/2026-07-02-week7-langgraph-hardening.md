# Week 7 LangGraph Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make invalid tool input exit deterministically, allow exactly five executed tool calls, align the Week 7 notebook with the corrected graph, and version all Week 7 deliverables.

**Architecture:** Preserve the explicit `StateGraph` with the prebuilt `ToolNode`, but add an `inspect_tools` node after tool execution and a dedicated `validation_exit` node. `route_after_agent` checks a projected call total before execution, while `inspect_tools` counts returned `ToolMessage` objects so `tool_calls` represents executions rather than model proposals.

**Tech Stack:** Python 3.13, LangGraph `StateGraph`, LangChain messages/tools, pytest, Jupyter Notebook, Git

---

## File Structure

- Modify `src/chains/langgraph_challenge_agent.py`: graph routing, post-tool accounting, deterministic validation exit.
- Modify `tests/test_langgraph_challenge_agent.py`: acceptance and regression coverage for execution count and validation routing.
- Modify `Week7_LangGraph_Challenge.ipynb`: graph explanation, traces, assertions, and LangSmith project assignment.
- Track `docs/superpowers/specs/2026-07-02-week7-langgraph-hardening-design.md`: approved design.
- Track `docs/superpowers/plans/2026-07-02-week7-langgraph-hardening.md`: this implementation plan.

### Task 1: Define the Correct Loop-Cap Behavior

**Files:**
- Modify: `tests/test_langgraph_challenge_agent.py:66-81`
- Test: `tests/test_langgraph_challenge_agent.py`

- [ ] **Step 1: Replace the existing loop-cap test with a five-executions regression test**

```python
from langchain_core.messages import AIMessage, ToolMessage


def test_loop_cap_executes_five_calls_and_blocks_the_sixth():
    responses = [
        _tool_call_message("add", {"a": index, "b": 1}, call_id=f"call_{index}")
        for index in range(MAX_TOOL_CALLS + 1)
    ]
    fake_llm = FakeToolCallingLLM(responses)
    app = build_graph(llm=fake_llm, checkpointer=InMemorySaver())

    result = app.invoke(
        initial_state("keep refining the number; try again and again"),
        config=_config("test-loop-cap"),
    )

    executed = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    assert len(executed) == MAX_TOOL_CALLS
    assert result["tool_calls"] == MAX_TOOL_CALLS
    assert len(fake_llm.calls) == MAX_TOOL_CALLS + 1
    assert "safety limit" in result["messages"][-1].content
    assert any(entry.startswith("guard=loop_cap") for entry in result["errors"])
```

- [ ] **Step 2: Run the new test and verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_langgraph_challenge_agent.py::test_loop_cap_executes_five_calls_and_blocks_the_sixth -q
```

Expected: FAIL because the current `>= MAX_TOOL_CALLS` route blocks the fifth tool call, leaving only four `ToolMessage` executions.

- [ ] **Step 3: Commit the failing test**

```powershell
git add tests/test_langgraph_challenge_agent.py
git commit -m "test: define week 7 tool execution cap"
```

### Task 2: Define Deterministic Validation Exit

**Files:**
- Modify: `tests/test_langgraph_challenge_agent.py:84-89`
- Test: `tests/test_langgraph_challenge_agent.py`

- [ ] **Step 1: Keep the direct tool test and add a full-graph validation test**

```python
def test_invalid_input_exits_without_another_llm_decision():
    fake_llm = FakeToolCallingLLM(
        [_tool_call_message("multiply", {"a": "abc", "b": 5}, call_id="call_invalid")]
    )
    app = build_graph(llm=fake_llm, checkpointer=InMemorySaver())

    result = app.invoke(
        initial_state("Multiply abc by 5."),
        config=_config("test-invalid-graph-input"),
    )

    assert len(fake_llm.calls) == 1
    assert result["tool_calls"] == 1
    assert any(entry.startswith("tool=multiply class=VALIDATION") for entry in result["errors"])
    assert "numeric" in result["messages"][-1].content.lower()
    assert "stopped" in result["messages"][-1].content.lower()
```

- [ ] **Step 2: Run the new test and verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_langgraph_challenge_agent.py::test_invalid_input_exits_without_another_llm_decision -q
```

Expected: FAIL because the current `tools -> agent` edge invokes the fake LLM a second time and exhausts its response list.

- [ ] **Step 3: Commit the failing test**

```powershell
git add tests/test_langgraph_challenge_agent.py
git commit -m "test: require deterministic validation exit"
```

### Task 3: Add Post-Tool Inspection and Correct Accounting

**Files:**
- Modify: `src/chains/langgraph_challenge_agent.py:106-205`
- Test: `tests/test_langgraph_challenge_agent.py`

- [ ] **Step 1: Add a trailing tool-message helper**

Insert before the node functions:

```python
def _trailing_tool_messages(messages: list[BaseMessage]) -> list[ToolMessage]:
    trailing: list[ToolMessage] = []
    for message in reversed(messages):
        if not isinstance(message, ToolMessage):
            break
        trailing.append(message)
    trailing.reverse()
    return trailing
```

- [ ] **Step 2: Restrict the agent node to model invocation**

Replace `agent_node` with:

```python
def make_agent_node(llm):
    """Build the agent node bound to a specific LLM (real or fake, for tests)."""

    def agent_node(state: AgentState) -> dict:
        return {"messages": [llm.invoke(state["messages"])]}

    return agent_node
```

- [ ] **Step 3: Check projected calls and allow exactly five executions**

Replace `route_after_agent` with:

```python
def route_after_agent(state: AgentState) -> str:
    base_route = tools_condition(state)
    if base_route != "tools":
        return END

    latest = state["messages"][-1]
    requested = len(getattr(latest, "tool_calls", None) or [])
    if state["tool_calls"] + requested > MAX_TOOL_CALLS:
        return "safe_exit"
    return "tools"
```

- [ ] **Step 4: Add post-tool accounting and error classification**

```python
def inspect_tools_node(state: AgentState) -> dict:
    tool_messages = _trailing_tool_messages(state["messages"])
    errors: list[str] = []
    retries = 0

    for message in tool_messages:
        content = message.content if isinstance(message.content, str) else str(message.content)
        if not content.startswith("ERROR:"):
            continue
        _, error_class, detail = content.split(":", 2)
        error_class = error_class.strip()
        errors.append(
            f"tool={message.name} class={error_class} detail={detail.strip()[:160]}"
        )
        if error_class == "TRANSIENT":
            retries += 1

    return {
        "tool_calls": len(tool_messages),
        "errors": errors,
        "retries": retries,
    }


def route_after_tools(state: AgentState) -> str:
    for message in _trailing_tool_messages(state["messages"]):
        content = message.content if isinstance(message.content, str) else str(message.content)
        if content.startswith("ERROR:VALIDATION:"):
            return "validation_exit"
    return "agent"
```

- [ ] **Step 5: Add the deterministic validation message**

```python
def validation_exit_node(state: AgentState) -> dict:
    details = []
    for message in _trailing_tool_messages(state["messages"]):
        content = message.content if isinstance(message.content, str) else str(message.content)
        if content.startswith("ERROR:VALIDATION:"):
            details.append(content.split(":", 2)[2].strip())

    detail = "; ".join(details) or "one or more tool arguments were invalid"
    return {
        "messages": [AIMessage(content=(
            f"I stopped the operation because the input was invalid: {detail}. "
            "Please provide numeric values and try again."
        ))]
    }
```

- [ ] **Step 6: Wire the new nodes and conditional edge**

Update graph construction to contain:

```python
workflow.add_node("agent", make_agent_node(llm))
workflow.add_node("tools", ToolNode(TOOLS))
workflow.add_node("inspect_tools", inspect_tools_node)
workflow.add_node("safe_exit", safe_exit_node)
workflow.add_node("validation_exit", validation_exit_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    route_after_agent,
    {"tools": "tools", "safe_exit": "safe_exit", END: END},
)
workflow.add_edge("tools", "inspect_tools")
workflow.add_conditional_edges(
    "inspect_tools",
    route_after_tools,
    {"agent": "agent", "validation_exit": "validation_exit"},
)
workflow.add_edge("safe_exit", END)
workflow.add_edge("validation_exit", END)
```

- [ ] **Step 7: Run both regression tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_langgraph_challenge_agent.py -q
```

Expected: `5 passed`.

- [ ] **Step 8: Commit the graph fix**

```powershell
git add src/chains/langgraph_challenge_agent.py
git commit -m "fix: harden week 7 langgraph routing"
```

### Task 4: Align Existing Tests With Executed-Call Semantics

**Files:**
- Modify: `tests/test_langgraph_challenge_agent.py:39-113`
- Test: `tests/test_langgraph_challenge_agent.py`

- [ ] **Step 1: Assert tool-message counts in math and replay tests**

Add to the math-chain test:

```python
executed = [message for message in result["messages"] if isinstance(message, ToolMessage)]
assert len(executed) == 2
assert result["tool_calls"] == len(executed)
```

Add to the replay test after resume:

```python
assert result["tool_calls"] == 1
```

- [ ] **Step 2: Run the targeted suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_langgraph_challenge_agent.py -q
```

Expected: `5 passed`.

- [ ] **Step 3: Commit the finalized tests**

```powershell
git add tests/test_langgraph_challenge_agent.py
git commit -m "test: cover week 7 guarded graph paths"
```

### Task 5: Update the Executed Week 7 Notebook

**Files:**
- Modify: `Week7_LangGraph_Challenge.ipynb`

- [ ] **Step 1: Correct the LangSmith project assignment**

Replace:

```python
os.environ.setdefault("LANGCHAIN_PROJECT", "Week7-LangGraph-Challenge")
```

with:

```python
os.environ["LANGCHAIN_PROJECT"] = "Week7-LangGraph-Challenge"
```

- [ ] **Step 2: Update architecture explanations**

Document the corrected flow exactly as:

```text
START -> agent
agent -> tools | safe_exit | END
tools -> inspect_tools
inspect_tools -> agent | validation_exit
safe_exit -> END
validation_exit -> END
```

Define `tool_calls` as completed tool executions counted from `ToolMessage`
objects. Explain that projected calls greater than five are blocked before
execution.

- [ ] **Step 3: Re-run all notebook cells from a clean kernel**

Use **Kernel -> Restart Kernel and Run All Cells**. Verify:

```text
LangSmith tracing ENABLED - project: Week7-LangGraph-Challenge
```

The loop-cap output must show five `tools` executions followed by a sixth
agent request and `safe_exit`. The invalid-input stream must show:

```text
agent -> tools -> inspect_tools -> validation_exit
```

with no second agent invocation.

- [ ] **Step 4: Commit the refreshed notebook**

```powershell
git add Week7_LangGraph_Challenge.ipynb
git commit -m "docs: refresh week 7 langgraph evidence"
```

### Task 6: Verify and Version the Complete Delivery

**Files:**
- Track: `Week7_LangGraph_Challenge.ipynb`
- Track: `src/chains/langgraph_challenge_agent.py`
- Track: `tests/test_langgraph_challenge_agent.py`
- Track: `docs/superpowers/specs/2026-07-02-week7-langgraph-hardening-design.md`
- Track: `docs/superpowers/plans/2026-07-02-week7-langgraph-hardening.md`

- [ ] **Step 1: Run the Week 7 tests**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_langgraph_challenge_agent.py -q
```

Expected: `5 passed`.

- [ ] **Step 2: Run the complete main suite**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: all tests pass; the two existing `create_react_agent` deprecation warnings may remain.

- [ ] **Step 3: Confirm only Week 7 files are selected for delivery**

```powershell
git status --short -- Week7_LangGraph_Challenge.ipynb src/chains/langgraph_challenge_agent.py tests/test_langgraph_challenge_agent.py docs/superpowers/specs/2026-07-02-week7-langgraph-hardening-design.md docs/superpowers/plans/2026-07-02-week7-langgraph-hardening.md
git diff --cached --stat
```

Expected: no unrelated BrunoAudioManager, notebook, backup, or local settings files are staged.

- [ ] **Step 4: Create a delivery commit only if tracked changes remain**

```powershell
git add Week7_LangGraph_Challenge.ipynb src/chains/langgraph_challenge_agent.py tests/test_langgraph_challenge_agent.py docs/superpowers/specs/2026-07-02-week7-langgraph-hardening-design.md docs/superpowers/plans/2026-07-02-week7-langgraph-hardening.md
git commit -m "feat: complete week 7 langgraph challenge"
```

- [ ] **Step 5: Do not push**

Report the local commit hashes and verification output. Remote publication requires a separate explicit user request.
