# Week 7 LangGraph Hardening Design

## Goal

Close the validation, loop-cap, observability, and Git-delivery gaps found during
the Week 7 review while preserving the explicit LangGraph `StateGraph` and
`ToolNode` architecture required by the challenge.

## Scope

The change is limited to:

- `src/chains/langgraph_challenge_agent.py`
- `tests/test_langgraph_challenge_agent.py`
- `Week7_LangGraph_Challenge.ipynb`

Unrelated project areas, including BrunoAudioManager, remain untouched. The
Week 7 artifacts will be staged for version control but will not be pushed.

## Graph Architecture

The graph will use this control flow:

```text
START -> agent
agent -> tools | safe_exit | END
tools -> inspect_tools
inspect_tools -> agent | validation_exit
safe_exit -> END
validation_exit -> END
```

The existing `agent` and prebuilt `ToolNode` remain responsible for model and
tool execution. A small `inspect_tools` node will account for completed tool
messages and classify their results. This keeps execution, accounting, and
error routing separate and directly testable.

## Tool-Call Limit

`tool_calls` will mean successfully attempted tool executions represented by
returned `ToolMessage` objects, not tool calls merely proposed by the model.
Before routing to `tools`, `route_after_agent` will calculate:

```text
projected calls = executed calls + calls requested by the latest AI message
```

The request is allowed when the projected total is at most
`MAX_TOOL_CALLS`. It is routed to `safe_exit` only when the projected total
would exceed the limit. With `MAX_TOOL_CALLS = 5`, five calls may execute and
the sixth is blocked.

When one AI message proposes more calls than the remaining allowance, the
whole batch is rejected. Partial execution of a parallel tool-call batch is
intentionally avoided because it could produce incomplete or misleading
results.

## Error Handling

Tools continue returning machine-readable error strings in the form:

```text
ERROR:<CLASS>: <detail>
```

After `ToolNode` completes, `inspect_tools` will inspect the trailing
`ToolMessage` block, increment `tool_calls`, append structured entries to
`errors`, and increment `retries` for `TRANSIENT` classifications.

A `VALIDATION` error routes deterministically to `validation_exit`. That node
will return a clear user-facing message explaining that the operation was
stopped, include concise validation detail, and suggest supplying numeric
inputs. It then exits without asking the LLM to decide whether to continue.

For the deterministic math tools, `TRANSIENT` remains a documented policy
classification rather than an active retry loop because these tools perform no
I/O and have no transient failure mode.

## Observability

The notebook will describe `tool_calls` as executed calls and update the graph
diagram, stream narratives, and assertions to include `inspect_tools` and
`validation_exit`. The invalid-input demonstration must show the deterministic
validation route.

The notebook will assign `LANGCHAIN_PROJECT` directly to
`Week7-LangGraph-Challenge` so existing environment values do not silently
send traces to another project.

## Testing

Tests will be written before production changes and observed failing for the
expected reasons. Coverage will include:

1. Five calls execute and a sixth request reaches `safe_exit`.
2. `tool_calls` equals the number of returned tool messages.
3. Invalid graph input records a structured validation error.
4. Invalid graph input ends through `validation_exit` without another LLM call.
5. Existing math-chain and checkpoint-resume behavior remains intact.

After targeted tests pass, the complete `tests` suite will run to detect
regressions.

## Delivery

The Week 7 notebook, implementation, tests, design, and implementation plan
will be added in focused commits. Existing unrelated modifications and
untracked files will not be staged. Publishing to a remote repository is out of
scope until explicitly requested.
