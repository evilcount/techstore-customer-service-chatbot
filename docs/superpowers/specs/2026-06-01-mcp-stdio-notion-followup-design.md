# MCP Stdio Notion Follow-up Server

## Scope

Add a formal Model Context Protocol server to the TechStore Plus Week 3 project. The
server exposes Notion follow-up task creation as an MCP tool over stdio.

This increment builds on the existing Notion follow-up integration in
`c03-t05-bruno-pieri-m1-challenge/` and must not change the mandatory Week 3 agent
behavior or make Notion required for `tests/test_stop3.py`.

## Goal

Provide a minimal but real MCP interface so compatible MCP clients can discover and call a
`create_followup_task` tool that creates a page in the configured Notion database.

## Architecture

Use the official Python MCP SDK with the stdio transport.

New files:

- `src/mcp/__init__.py`: marks the MCP package.
- `src/mcp/notion_followup_server.py`: creates a `FastMCP` server and registers the
  `create_followup_task` tool.
- `tests/test_mcp_notion_followup_unit.py`: tests payload conversion and tool behavior
  with a fake task client.

Existing code reused:

- `src.components.followup_detector.FollowUpTask`
- `src.integrations.notion_tasks.NotionTaskClient`

The MCP layer should be a thin adapter. Business logic remains in the existing detector
and Notion client modules.

## Tool Contract

Tool name:

- `create_followup_task`

Input fields:

- `task`: short title for the follow-up.
- `customer_email`: customer email address.
- `priority`: one of `low`, `medium`, `high`; default `medium`.
- `category`: one of `technical_support`, `billing`, `returns`, `product_inquiry`,
  `general_information`; default `general_information`.
- `description`: details to store in Notion; default empty string.
- `due_date`: optional ISO date string, `YYYY-MM-DD`.
- `source`: source label; default `mcp_stdio`.

Output:

- A concise string confirming the Notion page ID when task creation succeeds.
- A clear error string if configuration or task creation fails.

## Runtime

Run from `c03-t05-bruno-pieri-m1-challenge/`:

```powershell
..\.venv\Scripts\python.exe -m src.mcp.notion_followup_server
```

The process communicates over stdio using the MCP protocol. It must not print ordinary
debug output to stdout, because stdout is reserved for MCP JSON-RPC messages.

## Configuration

The server uses existing `.env` values:

- `NOTION_API_KEY`
- `NOTION_DATABASE_ID`

The server should call `load_dotenv()` at startup so local development picks up the root
project `.env`.

## Dependency

Add the official Python MCP SDK dependency to `requirements.txt`.

The implementation should import from the SDK in the smallest practical way, preferably
`FastMCP`, and avoid custom JSON-RPC implementation.

## Error Handling

Tool calls should not crash the MCP server for expected failures:

- Missing Notion credentials.
- Invalid `due_date`.
- Notion API errors.

Expected failures should be returned as clear tool text. Unexpected exceptions can also be
returned as an error string for this minimal server.

## Testing

Default tests must not require a live MCP client or real Notion API.

Add unit tests for:

- Building a `FollowUpTask` from MCP tool arguments.
- Invalid `due_date` returns an error.
- Tool handler uses an injected fake task client and returns the fake page ID.

Add a smoke test that imports the server module and verifies the app object exists.

The final verification should include:

```powershell
..\.venv\Scripts\python.exe -m pytest tests/test_mcp_notion_followup_unit.py tests/test_notion_tasks_unit.py tests/test_stop3.py -v
```

Optionally run the server manually with an MCP inspector or compatible MCP client after
the automated tests pass.

## Documentation

Update `README.md` with:

- MCP stdio server command.
- Tool name and fields.
- Required environment variables.
- Note that the existing `MemoryAgent` still uses the direct Notion integration, while
  the MCP server provides a formal external interface.

## Non-Goals

- Do not replace the existing `MemoryAgent` direct integration with an MCP client.
- Do not implement Streamable HTTP in this increment.
- Do not implement OAuth.
- Do not add tools for listing, updating, or deleting Notion tasks.
