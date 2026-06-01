# MCP Stdio Notion Follow-up Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a formal MCP stdio server that exposes Notion follow-up creation as a discoverable MCP tool.

**Architecture:** Create a thin `src/mcp/notion_followup_server.py` adapter using the official Python MCP SDK `FastMCP`. The MCP tool converts arguments into the existing `FollowUpTask` model and delegates persistence to the existing `NotionTaskClient`.

**Tech Stack:** Python 3.13, pytest, python-dotenv, official MCP Python SDK, existing Notion integration.

---

## Files

- Modify: `c03-t05-bruno-pieri-m1-challenge/requirements.txt`
- Create: `c03-t05-bruno-pieri-m1-challenge/src/mcp/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/src/mcp/notion_followup_server.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_mcp_notion_followup_unit.py`
- Modify: `c03-t05-bruno-pieri-m1-challenge/README.md`

---

### Task 1: Add MCP SDK Dependency

**Files:**
- Modify: `c03-t05-bruno-pieri-m1-challenge/requirements.txt`

- [ ] **Step 1: Check whether MCP SDK is installed**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -c "import mcp; print('mcp ok')"
```

Expected: either prints `mcp ok` or fails with `ModuleNotFoundError`.

- [ ] **Step 2: Install MCP SDK if missing**

If Step 1 fails, run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pip install mcp
```

Expected: installation succeeds.

- [ ] **Step 3: Add dependency to requirements**

Append this line to `requirements.txt` if it is not already present:

```text
mcp
```

- [ ] **Step 4: Verify import**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -c "from mcp.server.fastmcp import FastMCP; print('FastMCP ok')"
```

Expected: prints `FastMCP ok`.

- [ ] **Step 5: Commit dependency**

Run:

```powershell
git add requirements.txt
git commit -m "chore: add mcp sdk dependency"
```

---

### Task 2: Add MCP Follow-up Server Unit Tests

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_mcp_notion_followup_unit.py`
- Create later: `c03-t05-bruno-pieri-m1-challenge/src/mcp/__init__.py`
- Create later: `c03-t05-bruno-pieri-m1-challenge/src/mcp/notion_followup_server.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_mcp_notion_followup_unit.py`:

```python
from datetime import date

from src.components.followup_detector import FollowUpTask
from src.mcp.notion_followup_server import (
    app,
    build_followup_task,
    create_followup_task,
)


class FakeTaskClient:
    def __init__(self):
        self.created = []

    def create_task(self, task):
        self.created.append(task)
        return "page-123"


class FailingTaskClient:
    def create_task(self, task):
        raise RuntimeError("notion unavailable")


def test_app_exists_for_mcp_server():
    assert app.name == "techstore-notion-followups"


def test_build_followup_task_from_tool_arguments():
    task = build_followup_task(
        task="Check refund tomorrow",
        customer_email="sarah.smith@company.com",
        priority="high",
        category="billing",
        description="Customer asked for refund follow-up.",
        due_date="2026-06-02",
        source="mcp_stdio",
    )

    assert isinstance(task, FollowUpTask)
    assert task.task == "Check refund tomorrow"
    assert task.customer_email == "sarah.smith@company.com"
    assert task.priority == "high"
    assert task.status == "open"
    assert task.category == "billing"
    assert task.description == "Customer asked for refund follow-up."
    assert task.due_date == date(2026, 6, 2)
    assert task.source == "mcp_stdio"


def test_create_followup_task_uses_injected_client():
    fake_client = FakeTaskClient()

    result = create_followup_task(
        task="Check ticket tomorrow",
        customer_email="john.doe@company.com",
        priority="medium",
        category="general_information",
        description="Customer asked for ticket follow-up.",
        due_date=None,
        source="mcp_stdio",
        task_client=fake_client,
    )

    assert result == "Notion follow-up created: page-123"
    assert len(fake_client.created) == 1
    assert fake_client.created[0].task == "Check ticket tomorrow"


def test_create_followup_task_returns_error_for_invalid_due_date():
    result = create_followup_task(
        task="Check ticket",
        customer_email="john.doe@company.com",
        due_date="tomorrow",
        task_client=FakeTaskClient(),
    )

    assert "Invalid due_date" in result


def test_create_followup_task_returns_error_when_client_fails():
    result = create_followup_task(
        task="Check ticket",
        customer_email="john.doe@company.com",
        task_client=FailingTaskClient(),
    )

    assert "Notion follow-up could not be created" in result
    assert "notion unavailable" in result
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_mcp_notion_followup_unit.py -v
```

Expected: fails with `ModuleNotFoundError: No module named 'src.mcp'`.

---

### Task 3: Implement MCP Stdio Server

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/src/mcp/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/src/mcp/notion_followup_server.py`
- Test: `c03-t05-bruno-pieri-m1-challenge/tests/test_mcp_notion_followup_unit.py`

- [ ] **Step 1: Create MCP package and server**

Create `src/mcp/__init__.py` as an empty file.

Create `src/mcp/notion_followup_server.py`:

```python
from __future__ import annotations

from datetime import date
from typing import Protocol

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.components.followup_detector import FollowUpTask
from src.integrations.notion_tasks import NotionTaskClient

load_dotenv()

app = FastMCP("techstore-notion-followups")


class TaskClient(Protocol):
    def create_task(self, task: FollowUpTask) -> str:
        ...


def build_followup_task(
    task: str,
    customer_email: str,
    priority: str = "medium",
    category: str = "general_information",
    description: str = "",
    due_date: str | None = None,
    source: str = "mcp_stdio",
) -> FollowUpTask:
    parsed_due_date = date.fromisoformat(due_date) if due_date else None
    return FollowUpTask(
        task=task,
        customer_email=customer_email,
        priority=priority,
        status="open",
        category=category,
        due_date=parsed_due_date,
        description=description,
        source=source,
    )


def create_followup_task(
    task: str,
    customer_email: str,
    priority: str = "medium",
    category: str = "general_information",
    description: str = "",
    due_date: str | None = None,
    source: str = "mcp_stdio",
    task_client: TaskClient | None = None,
) -> str:
    try:
        followup_task = build_followup_task(
            task=task,
            customer_email=customer_email,
            priority=priority,
            category=category,
            description=description,
            due_date=due_date,
            source=source,
        )
    except ValueError:
        return "Invalid due_date. Use ISO format YYYY-MM-DD."

    client = task_client or NotionTaskClient.from_env()
    try:
        page_id = client.create_task(followup_task)
    except Exception as exc:
        return f"Notion follow-up could not be created: {exc}"

    return f"Notion follow-up created: {page_id}"


@app.tool()
def create_followup_task_tool(
    task: str,
    customer_email: str,
    priority: str = "medium",
    category: str = "general_information",
    description: str = "",
    due_date: str | None = None,
    source: str = "mcp_stdio",
) -> str:
    """Create a TechStore Plus customer follow-up task in Notion."""
    return create_followup_task(
        task=task,
        customer_email=customer_email,
        priority=priority,
        category=category,
        description=description,
        due_date=due_date,
        source=source,
    )


def main() -> None:
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run MCP unit tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_mcp_notion_followup_unit.py -v
```

Expected: all MCP unit tests pass.

- [ ] **Step 3: Verify module imports**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -c "from src.mcp.notion_followup_server import app; print(app.name)"
```

Expected: prints `techstore-notion-followups`.

- [ ] **Step 4: Commit MCP server**

Run:

```powershell
git add src/mcp/__init__.py src/mcp/notion_followup_server.py tests/test_mcp_notion_followup_unit.py
git commit -m "feat: add mcp stdio notion followup server"
```

---

### Task 4: Update README for MCP Server

**Files:**
- Modify: `c03-t05-bruno-pieri-m1-challenge/README.md`

- [ ] **Step 1: Add MCP documentation**

Append under the existing Notion follow-up documentation:

```markdown
### MCP Stdio Server

The project also exposes the Notion follow-up workflow as a formal MCP server over
stdio. Run it from this directory:

```powershell
..\.venv\Scripts\python.exe -m src.mcp.notion_followup_server
```

The MCP server provides one tool:

`create_followup_task`

Fields:

- `task`: short follow-up title.
- `customer_email`: customer email address.
- `priority`: `low`, `medium`, or `high`.
- `category`: `technical_support`, `billing`, `returns`, `product_inquiry`, or
  `general_information`.
- `description`: details to save in Notion.
- `due_date`: optional ISO date, for example `2026-06-02`.
- `source`: defaults to `mcp_stdio`.

The server uses `NOTION_API_KEY` and `NOTION_DATABASE_ID` from `.env`. The existing
`MemoryAgent` still uses the direct Notion integration; the MCP server is an external
standard interface for compatible MCP clients.
```

- [ ] **Step 2: Run README-neutral tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_mcp_notion_followup_unit.py tests/test_notion_tasks_unit.py -v
```

Expected: tests pass.

- [ ] **Step 3: Commit README**

Run:

```powershell
git add README.md
git commit -m "docs: document mcp stdio notion server"
```

---

### Task 5: Final Verification

**Files:**
- Test: `c03-t05-bruno-pieri-m1-challenge/tests/test_mcp_notion_followup_unit.py`
- Test: existing Week 3 and Notion test suite

- [ ] **Step 1: Run full relevant test suite**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_customer_tools_unit.py tests/test_hybrid_memory_unit.py tests/test_stop3.py tests/test_followup_detector_unit.py tests/test_notion_tasks_unit.py tests/test_memory_agent_followup_unit.py tests/test_mcp_notion_followup_unit.py -v
```

Expected: all tests pass.

- [ ] **Step 2: Verify MCP module command imports without starting stdio loop**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -c "from src.mcp.notion_followup_server import app; print(app.name)"
```

Expected: prints `techstore-notion-followups`.

- [ ] **Step 3: Check git status**

Run:

```powershell
git status --short --branch
```

Expected: no uncommitted changes in `c03-t05-bruno-pieri-m1-challenge`.

- [ ] **Step 4: Report result**

Report:

```text
MCP stdio Notion follow-up server implemented.
Tool exposed: create_followup_task.
Tests passed: <count>.
Manual command: ..\.venv\Scripts\python.exe -m src.mcp.notion_followup_server
```
