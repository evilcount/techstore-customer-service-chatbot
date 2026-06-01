# Week 3 MVP: Advanced Memory and Tools

## Scope

Implement the mandatory Week 3 MVP for the TechStore Plus customer service agent in
`c03-t05-bruno-pieri-m1-challenge/`.

The MVP includes:

- `HybridMemory`: manual message-list memory with capped recent buffer, rolling summary,
  per-customer context, and `trim_messages`.
- `MockCustomerDB` plus six `@tool` functions for customer, order, tracking, ticket, and
  ticket creation workflows.
- `MemoryAgent`: a tool-using LangChain agent with one isolated `HybridMemory` instance
  per customer email.
- Passing the three mandatory tests in `tests/test_stop3.py`.

MCP task automation is intentionally out of scope for this MVP. It is the next follow-up
after the mandatory tests pass.

## Backup

Before implementation, a source backup was created under `backups/`:

- `techstore-chatbot-source-backup-20260601-160850.zip`

The backup excludes generated or heavy local directories (`.git`, `.venv`, caches, and the
`backups` directory itself) and keeps the project files that will be edited.

## Approach

Use the existing starter structure in `c03-t05-bruno-pieri-m1-challenge/src/` because it
matches the Week 3 PDF requirements and already contains the intended module boundaries:

- `src/components/hybrid_memory.py`
- `src/components/customer_tools.py`
- `src/chains/memory_agent.py`
- `src/database/mock_db.py`
- `tests/test_stop3.py`

This keeps the implementation aligned with the rubric and avoids moving the Week 3 work
into notebooks where automated validation is harder.

## Architecture

`MemoryAgent.chat(customer_email, user_text)` is the main entry point.

Flow:

1. Retrieve or create the `HybridMemory` for `customer_email`.
2. Append the user message to that customer's memory.
3. Build the message list with `HybridMemory.build_messages()`.
4. Invoke the LangChain tool-using agent with `{"messages": messages}`.
5. Extract the final AI response from the returned message list.
6. Append only the final AI message to memory.
7. Return the final response content.

Each email key owns a separate memory object. This prevents cross-customer leakage and
matches the mandatory memory isolation test.

## HybridMemory Design

`HybridMemory` stores:

- `CustomerContext`: email, name, category, preferences, and previous issues.
- `_buffer`: recent `HumanMessage` and final `AIMessage` entries.
- `running_summary`: concise factual summary of displaced older turns.

When `_buffer` exceeds `BUFFER_SIZE`, the oldest user/assistant pair is removed and folded
into `running_summary` with a cheap summarizer model. Keeping customer metadata outside
the message buffer ensures identity and account context survive trimming and summary
updates.

`build_messages()` returns:

1. A `SystemMessage` with TechStore Plus instructions, customer context, and any running
   summary.
2. The recent verbatim buffer.
3. A final list processed through `trim_messages` with `include_system=True`.

This design preserves recent precision while controlling prompt growth.

## Tools Design

The six tool functions wrap `MockCustomerDB` helpers and return clear, human-readable
strings:

- `get_customer_info(email)`
- `get_order_status(order_number)`
- `get_shipping_tracking(order_number)`
- `get_customer_orders(email)`
- `get_customer_tickets(email)`
- `create_support_ticket(email, category, priority, description)`

Tools must not crash on unknown data. Missing customer, order, tracking, or ticket data
returns a clear message that the agent can use in its final answer.

## Error Handling

Expected failures are handled as plain tool responses:

- Unknown email: no account found, or ticket creation cannot proceed.
- Unknown order number: order not found.
- Unshipped or cancelled order: explain that no tracking number is available and include
  current status.
- Customer with no orders or tickets: return an explicit empty-result message.

The agent layer should avoid swallowing unexpected exceptions during development so test
failures remain visible.

## Testing

Run from `c03-t05-bruno-pieri-m1-challenge/`:

```powershell
python -m pytest tests/test_stop3.py -v
```

Mandatory pass criteria:

- Test Case A: John and Sarah have isolated memory buffers and no conversation leakage.
- Test Case B: John asks about `TEC-2024-001`, gets `in_transit`, then asks "When will it
  arrive?" without repeating the order number.
- Test Case C: Emily's buffer overflows, older turns are summarized, and the agent can
  recall the original Mac Mini issue from the summary.

These tests use `ChatOpenAI`, so a valid `OPENAI_API_KEY` in `.env` is required for full
verification.

## Documentation Updates

After implementation, update the Week 3 README with:

- MVP architecture.
- Setup and environment variables.
- How to run `pytest`.
- Known limitation: in-memory only, no persistence across process restarts.
- Follow-up note: MCP task automation will be implemented after the mandatory MVP passes.

## Deferred Follow-Up: MCP

After the MVP tests pass, implement the bonus MCP task automation. The follow-up should
detect future-action intents in agent responses or user requests and create tasks through
an MCP-compatible target without changing the core memory and tools behavior.
