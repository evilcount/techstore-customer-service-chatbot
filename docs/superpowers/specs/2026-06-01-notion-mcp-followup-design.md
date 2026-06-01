# Notion MCP Follow-up Integration

## Scope

Implement the Week 3 follow-up increment for the TechStore Plus customer service
agent: create customer follow-up tasks in a Notion database when a customer asks for
future action.

This increment targets the existing package in `c03-t05-bruno-pieri-m1-challenge/`.
The mandatory Week 3 MVP behavior must remain unchanged and the existing tests must
continue to pass.

## External Target

The external task destination is a Notion database named `TechStore Plus Follow-ups`.
The project reads credentials from `.env`:

- `NOTION_API_KEY`: Notion internal connection token.
- `NOTION_DATABASE_ID`: Notion database ID.

The Notion connection must have access to the database and content capabilities for
reading, inserting, and updating content.

## Database Contract

The Notion database must expose these properties:

- `Task`: title
- `Customer Email`: email or rich text
- `Priority`: select with `low`, `medium`, `high`
- `Status`: select with `open`, `in_progress`, `done`
- `Category`: select with `technical_support`, `billing`, `returns`,
  `product_inquiry`, `general_information`
- `Due Date`: date
- `Description`: rich text
- `Source`: rich text

The integration creates pages with `Status` set to `open` by default.

## Architecture

Use a local Notion task adapter plus deterministic follow-up detection.

New code should live in small focused modules:

- `src/integrations/notion_tasks.py`: Notion task model and API client.
- `src/components/followup_detector.py`: deterministic extraction of follow-up task
  intent from the user message and assistant reply.
- `src/chains/memory_agent.py`: optional dependency injection of the task client and
  a post-response hook that creates a task when the detector returns one.

This is intentionally not exposed as another LangChain tool in the first version. The
agent should not need to decide whether to call Notion; the deterministic post-response
hook keeps tests stable and avoids changing the required tool-use behavior that already
passes `tests/test_stop3.py`.

## Data Flow

`MemoryAgent.chat(customer_email, user_text)` continues to:

1. Load the customer's `HybridMemory`.
2. Append the user message.
3. Invoke the LangChain tool agent.
4. Append the final assistant message.
5. Return the assistant text.

The follow-up increment adds a post-response step:

1. Call `detect_followup_task(customer_email, user_text, assistant_reply)`.
2. If no task is detected, return the original assistant text.
3. If a task is detected and a task client is configured, call
   `task_client.create_task(task)`.
4. Return the assistant text with a short confirmation that a Notion follow-up was
   created.
5. If task creation fails because credentials are missing or Notion rejects the request,
   return the assistant text with a short note that the follow-up could not be created.

The Notion result is not stored in conversation memory beyond the final returned
assistant message, preserving the existing memory behavior.

## Follow-up Detection

The detector is intentionally simple and deterministic. It should detect customer
messages containing future-action intent, including Portuguese and English phrases such
as:

- `crie um follow-up`
- `criar um follow-up`
- `me lembre`
- `lembre-me`
- `acompanhe`
- `verifique amanhã`
- `check tomorrow`
- `follow up`
- `remind me`

The initial task fields are inferred conservatively:

- `task`: concise title from the user request, capped to a short sentence.
- `customer_email`: the email passed to `MemoryAgent.chat`.
- `priority`: `high` if the message contains urgency words like `urgente` or
  `emergency`; otherwise `medium`.
- `status`: `open`.
- `category`: `general_information` unless the message contains clear words for billing,
  returns, technical support, or product inquiry.
- `due_date`: tomorrow if the message contains `amanhã` or `tomorrow`; otherwise omitted.
- `description`: include the original user request and a short excerpt of the assistant
  reply.
- `source`: `memory_agent`.

The detector should avoid creating tasks for ordinary support questions that do not ask
for future action.

## Error Handling

The Notion client should raise clear Python exceptions for configuration or API failures.
The agent integration should catch those exceptions so customer service replies still
complete.

Expected failure cases:

- Missing `NOTION_API_KEY` or `NOTION_DATABASE_ID`.
- Notion database not shared with the integration.
- Database property names do not match the expected contract.
- Network/API failure.

Unit tests should assert that these failures do not crash `MemoryAgent.chat` when a fake
client is injected.

## Testing

Tests should not depend on the real Notion API by default.

Add unit tests for:

- `detect_followup_task` returns `None` for a normal support question.
- `detect_followup_task` returns a `FollowUpTask` for Portuguese follow-up language.
- Due date inference for `amanhã` or `tomorrow`.
- Category and priority inference.
- `NotionTaskClient` payload building for the configured database schema.
- `MemoryAgent` calls an injected fake task client when a follow-up is detected.
- `MemoryAgent` preserves the original reply when the fake task client raises.

Add an optional integration test marked with `pytest.mark.integration` that calls the
real Notion API only when both Notion environment variables are set. This test should be
safe to skip in normal automated runs.

The final verification command remains:

```powershell
..\.venv\Scripts\python.exe -m pytest tests/test_customer_tools_unit.py tests/test_hybrid_memory_unit.py tests/test_stop3.py tests/test_followup_detector_unit.py tests/test_notion_tasks_unit.py -v
```

## Documentation

Update `README.md` with:

- Required Notion environment variables.
- Expected Notion database properties.
- A sample customer prompt that creates a follow-up task.
- Note that MCP/Notion task creation is a bonus follow-up increment and the core memory
  agent still works without Notion credentials.

## Non-Goals

- Do not build a public OAuth Notion app.
- Do not add Trello, Jira, Google Tasks, or other task destinations.
- Do not make Notion task creation a required dependency for the Week 3 mandatory tests.
- Do not persist conversation memory outside the process.
