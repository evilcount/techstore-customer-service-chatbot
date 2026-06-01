# Notion MCP Follow-up Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional Notion follow-up task creation to the TechStore Plus memory agent without breaking the mandatory Week 3 MVP tests.

**Architecture:** Add a deterministic follow-up detector and a small Notion task client under `c03-t05-bruno-pieri-m1-challenge/src/`. `MemoryAgent` receives an optional task client and creates a Notion task after normal agent response generation when the detector finds future-action intent.

**Tech Stack:** Python 3.13, pytest, python-dotenv, requests, Notion API, LangChain/LangGraph existing agent code.

---

## Files

- Create: `c03-t05-bruno-pieri-m1-challenge/src/integrations/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/src/integrations/notion_tasks.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/src/components/followup_detector.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_followup_detector_unit.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_notion_tasks_unit.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_memory_agent_followup_unit.py`
- Modify: `c03-t05-bruno-pieri-m1-challenge/src/chains/memory_agent.py`
- Modify: `c03-t05-bruno-pieri-m1-challenge/README.md`

Do not make Notion credentials required for `tests/test_stop3.py`.

---

### Task 1: Add Follow-up Detector

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/src/components/followup_detector.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_followup_detector_unit.py`

- [ ] **Step 1: Write failing detector tests**

Create `tests/test_followup_detector_unit.py`:

```python
from datetime import date, timedelta

from src.components.followup_detector import detect_followup_task


def test_detect_followup_returns_none_for_normal_support_question():
    task = detect_followup_task(
        customer_email="john.doe@company.com",
        user_text="What's the status of order TEC-2024-001?",
        assistant_reply="Order TEC-2024-001 is in_transit.",
    )

    assert task is None


def test_detect_followup_from_portuguese_request():
    task = detect_followup_task(
        customer_email="john.doe@company.com",
        user_text="Pode criar um follow-up para verificar meu ticket amanhã?",
        assistant_reply="Claro, vou acompanhar isso.",
    )

    assert task is not None
    assert task.task == "Verificar meu ticket amanhã"
    assert task.customer_email == "john.doe@company.com"
    assert task.priority == "medium"
    assert task.status == "open"
    assert task.category == "general_information"
    assert task.source == "memory_agent"
    assert task.due_date == date.today() + timedelta(days=1)
    assert "Pode criar um follow-up" in task.description
    assert "Claro" in task.description


def test_detect_followup_from_english_request():
    task = detect_followup_task(
        customer_email="sarah.smith@company.com",
        user_text="Remind me to check tomorrow if my refund was processed.",
        assistant_reply="I can help you keep track of that.",
    )

    assert task is not None
    assert task.customer_email == "sarah.smith@company.com"
    assert task.due_date == date.today() + timedelta(days=1)
    assert task.category == "billing"


def test_detect_followup_infers_high_priority():
    task = detect_followup_task(
        customer_email="emily.brown@company.com",
        user_text="Crie um follow-up urgente sobre meu Mac Mini que não liga.",
        assistant_reply="Entendi o problema.",
    )

    assert task is not None
    assert task.priority == "high"
    assert task.category == "technical_support"
```

- [ ] **Step 2: Run detector tests and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_followup_detector_unit.py -v
```

Expected: fail with `ModuleNotFoundError: No module named 'src.components.followup_detector'`.

- [ ] **Step 3: Implement minimal detector**

Create `src/components/followup_detector.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class FollowUpTask:
    task: str
    customer_email: str
    priority: str = "medium"
    status: str = "open"
    category: str = "general_information"
    due_date: date | None = None
    description: str = ""
    source: str = "memory_agent"


FOLLOWUP_PHRASES = (
    "crie um follow-up",
    "criar um follow-up",
    "follow-up",
    "follow up",
    "me lembre",
    "lembre-me",
    "acompanhe",
    "verifique amanhã",
    "check tomorrow",
    "remind me",
)

HIGH_PRIORITY_WORDS = ("urgente", "emergency", "asap", "imediato")

CATEGORY_KEYWORDS = (
    ("billing", ("refund", "invoice", "payment", "billing", "reembolso", "pagamento", "cobrança", "cobranca")),
    ("returns", ("return", "returns", "devolução", "devolucao", "troca")),
    ("technical_support", ("technical", "support", "mac mini", "não liga", "nao liga", "power", "laptop", "router")),
    ("product_inquiry", ("product", "produto", "stock", "estoque", "recommendation", "recomendação", "recomendacao")),
)


def detect_followup_task(
    customer_email: str,
    user_text: str,
    assistant_reply: str,
) -> FollowUpTask | None:
    normalized = user_text.lower()
    if not any(phrase in normalized for phrase in FOLLOWUP_PHRASES):
        return None

    return FollowUpTask(
        task=_build_title(user_text),
        customer_email=customer_email,
        priority=_infer_priority(normalized),
        category=_infer_category(normalized),
        due_date=_infer_due_date(normalized),
        description=_build_description(user_text, assistant_reply),
    )


def _build_title(user_text: str) -> str:
    title = user_text.strip().rstrip(".?!")
    replacements = (
        "Pode criar um follow-up para ",
        "pode criar um follow-up para ",
        "Crie um follow-up para ",
        "crie um follow-up para ",
        "Crie um follow-up ",
        "crie um follow-up ",
        "Remind me to ",
        "remind me to ",
    )
    for prefix in replacements:
        if title.startswith(prefix):
            title = title[len(prefix):]
            break
    title = title[:1].upper() + title[1:]
    return title[:80]


def _infer_priority(normalized_text: str) -> str:
    if any(word in normalized_text for word in HIGH_PRIORITY_WORDS):
        return "high"
    return "medium"


def _infer_category(normalized_text: str) -> str:
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in normalized_text for keyword in keywords):
            return category
    return "general_information"


def _infer_due_date(normalized_text: str) -> date | None:
    if "amanhã" in normalized_text or "amanha" in normalized_text or "tomorrow" in normalized_text:
        return date.today() + timedelta(days=1)
    return None


def _build_description(user_text: str, assistant_reply: str) -> str:
    reply_excerpt = assistant_reply.strip()[:300]
    return f"Customer request: {user_text.strip()}\n\nAssistant reply: {reply_excerpt}"
```

- [ ] **Step 4: Run detector tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_followup_detector_unit.py -v
```

Expected: all detector tests pass.

- [ ] **Step 5: Commit detector**

Run:

```powershell
git add src/components/followup_detector.py tests/test_followup_detector_unit.py
git commit -m "feat: detect followup task requests"
```

---

### Task 2: Add Notion Task Client

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/src/integrations/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/src/integrations/notion_tasks.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_notion_tasks_unit.py`

- [ ] **Step 1: Write failing Notion payload tests**

Create `tests/test_notion_tasks_unit.py`:

```python
from datetime import date

import pytest

from src.components.followup_detector import FollowUpTask
from src.integrations.notion_tasks import NotionConfigError, NotionTaskClient


def test_build_payload_maps_task_to_notion_properties():
    client = NotionTaskClient(api_key="secret_test", database_id="db123")
    task = FollowUpTask(
        task="Check refund tomorrow",
        customer_email="sarah.smith@company.com",
        priority="high",
        status="open",
        category="billing",
        due_date=date(2026, 6, 2),
        description="Customer asked for refund follow-up.",
        source="memory_agent",
    )

    payload = client.build_payload(task)

    assert payload["parent"] == {"database_id": "db123"}
    assert payload["properties"]["Task"]["title"][0]["text"]["content"] == "Check refund tomorrow"
    assert payload["properties"]["Customer Email"]["email"] == "sarah.smith@company.com"
    assert payload["properties"]["Priority"]["select"]["name"] == "high"
    assert payload["properties"]["Status"]["select"]["name"] == "open"
    assert payload["properties"]["Category"]["select"]["name"] == "billing"
    assert payload["properties"]["Due Date"]["date"]["start"] == "2026-06-02"
    assert payload["properties"]["Description"]["rich_text"][0]["text"]["content"] == "Customer asked for refund follow-up."
    assert payload["properties"]["Source"]["rich_text"][0]["text"]["content"] == "memory_agent"


def test_build_payload_omits_due_date_when_missing():
    client = NotionTaskClient(api_key="secret_test", database_id="db123")
    task = FollowUpTask(task="Check ticket", customer_email="john.doe@company.com")

    payload = client.build_payload(task)

    assert "Due Date" not in payload["properties"]


def test_from_env_requires_api_key(monkeypatch):
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    monkeypatch.setenv("NOTION_DATABASE_ID", "db123")

    with pytest.raises(NotionConfigError, match="NOTION_API_KEY"):
        NotionTaskClient.from_env()


def test_from_env_requires_database_id(monkeypatch):
    monkeypatch.setenv("NOTION_API_KEY", "secret_test")
    monkeypatch.delenv("NOTION_DATABASE_ID", raising=False)

    with pytest.raises(NotionConfigError, match="NOTION_DATABASE_ID"):
        NotionTaskClient.from_env()
```

- [ ] **Step 2: Run Notion tests and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_notion_tasks_unit.py -v
```

Expected: fail with `ModuleNotFoundError: No module named 'src.integrations'`.

- [ ] **Step 3: Implement Notion client**

Create `src/integrations/__init__.py` as an empty file.

Create `src/integrations/notion_tasks.py`:

```python
from __future__ import annotations

import os
from typing import Any

import requests

from src.components.followup_detector import FollowUpTask

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"


class NotionConfigError(RuntimeError):
    """Raised when Notion credentials are missing."""


class NotionTaskError(RuntimeError):
    """Raised when Notion rejects a task creation request."""


class NotionTaskClient:
    def __init__(
        self,
        api_key: str,
        database_id: str,
        *,
        session: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.database_id = database_id
        self._session = session or requests.Session()

    @classmethod
    def from_env(cls) -> "NotionTaskClient":
        api_key = os.getenv("NOTION_API_KEY")
        database_id = os.getenv("NOTION_DATABASE_ID")
        if not api_key:
            raise NotionConfigError("NOTION_API_KEY is not set.")
        if not database_id:
            raise NotionConfigError("NOTION_DATABASE_ID is not set.")
        return cls(api_key=api_key, database_id=database_id)

    def build_payload(self, task: FollowUpTask) -> dict[str, Any]:
        properties: dict[str, Any] = {
            "Task": {"title": [{"text": {"content": task.task}}]},
            "Customer Email": {"email": task.customer_email},
            "Priority": {"select": {"name": task.priority}},
            "Status": {"select": {"name": task.status}},
            "Category": {"select": {"name": task.category}},
            "Description": {"rich_text": [{"text": {"content": task.description}}]},
            "Source": {"rich_text": [{"text": {"content": task.source}}]},
        }
        if task.due_date is not None:
            properties["Due Date"] = {"date": {"start": task.due_date.isoformat()}}

        return {
            "parent": {"database_id": self.database_id},
            "properties": properties,
        }

    def create_task(self, task: FollowUpTask) -> str:
        response = self._session.post(
            NOTION_API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
            json=self.build_payload(task),
            timeout=30,
        )
        if response.status_code >= 400:
            raise NotionTaskError(
                f"Notion task creation failed with {response.status_code}: {response.text}"
            )
        data = response.json()
        return str(data.get("id", ""))
```

- [ ] **Step 4: Run Notion tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_notion_tasks_unit.py -v
```

Expected: all Notion unit tests pass.

- [ ] **Step 5: Commit Notion client**

Run:

```powershell
git add src/integrations/__init__.py src/integrations/notion_tasks.py tests/test_notion_tasks_unit.py
git commit -m "feat: add notion task client"
```

---

### Task 3: Integrate Follow-ups Into MemoryAgent

**Files:**
- Modify: `c03-t05-bruno-pieri-m1-challenge/src/chains/memory_agent.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/tests/test_memory_agent_followup_unit.py`

- [ ] **Step 1: Write failing MemoryAgent follow-up tests**

Create `tests/test_memory_agent_followup_unit.py`:

```python
from langchain_core.messages import AIMessage

from src.chains.memory_agent import MemoryAgent


class FakeGraphAgent:
    def invoke(self, payload):
        return {"messages": [*payload["messages"], AIMessage(content="I'll help track that.")]}


class FakeTaskClient:
    def __init__(self):
        self.created = []

    def create_task(self, task):
        self.created.append(task)
        return "notion-page-id"


class FailingTaskClient:
    def create_task(self, task):
        raise RuntimeError("notion unavailable")


def build_agent(task_client):
    agent = MemoryAgent(task_client=task_client)
    agent._agent = FakeGraphAgent()
    return agent


def test_chat_creates_followup_task_with_injected_client():
    task_client = FakeTaskClient()
    agent = build_agent(task_client)

    reply = agent.chat(
        "john.doe@company.com",
        "Pode criar um follow-up para verificar meu ticket amanhã?",
    )

    assert "I'll help track that." in reply
    assert "Notion follow-up created" in reply
    assert len(task_client.created) == 1
    assert task_client.created[0].customer_email == "john.doe@company.com"
    assert task_client.created[0].task == "Verificar meu ticket amanhã"


def test_chat_does_not_create_task_for_normal_message():
    task_client = FakeTaskClient()
    agent = build_agent(task_client)

    reply = agent.chat("john.doe@company.com", "Hello, can you help me?")

    assert reply == "I'll help track that."
    assert task_client.created == []


def test_chat_preserves_reply_when_task_creation_fails():
    agent = build_agent(FailingTaskClient())

    reply = agent.chat(
        "john.doe@company.com",
        "Pode criar um follow-up para verificar meu ticket amanhã?",
    )

    assert "I'll help track that." in reply
    assert "Notion follow-up could not be created" in reply
```

- [ ] **Step 2: Run MemoryAgent follow-up tests and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_memory_agent_followup_unit.py -v
```

Expected: fail because `MemoryAgent.__init__()` does not accept `task_client`.

- [ ] **Step 3: Update MemoryAgent**

Modify `src/chains/memory_agent.py` imports:

```python
from typing import Protocol

from src.components.followup_detector import FollowUpTask, detect_followup_task
from src.integrations.notion_tasks import NotionConfigError, NotionTaskClient
```

Add protocol above `MemoryAgent`:

```python
class TaskClient(Protocol):
    def create_task(self, task: FollowUpTask) -> str:
        ...
```

Replace `__init__` with:

```python
    def __init__(self, task_client: TaskClient | None = None) -> None:
        self._llm = ChatOpenAI(model=MODEL, temperature=0)
        # create_react_agent builds a LangGraph ReAct loop:
        # model call → tool execution (if needed) → model call → final answer
        self._agent = create_react_agent(self._llm, tools=TOOLS)
        # One HybridMemory instance per customer email — never share between customers
        self._memories: dict[str, HybridMemory] = {}
        self._task_client = task_client
```

Replace the end of `chat` after `memory.append_assistant(reply)` with:

```python
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
```

- [ ] **Step 4: Run MemoryAgent follow-up tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_memory_agent_followup_unit.py -v
```

Expected: all MemoryAgent follow-up tests pass.

- [ ] **Step 5: Run existing mandatory tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_stop3.py -v
```

Expected: all mandatory Week 3 tests still pass.

- [ ] **Step 6: Commit MemoryAgent integration**

Run:

```powershell
git add src/chains/memory_agent.py tests/test_memory_agent_followup_unit.py
git commit -m "feat: create notion followups from memory agent"
```

---

### Task 4: Add Optional Real Notion Smoke Test

**Files:**
- Modify: `c03-t05-bruno-pieri-m1-challenge/tests/test_notion_tasks_unit.py`

- [ ] **Step 1: Add skipped-by-default integration test**

Append to `tests/test_notion_tasks_unit.py`:

```python
import os


@pytest.mark.integration
def test_create_task_against_real_notion_database():
    if not os.getenv("NOTION_API_KEY") or not os.getenv("NOTION_DATABASE_ID"):
        pytest.skip("NOTION_API_KEY and NOTION_DATABASE_ID are required.")

    client = NotionTaskClient.from_env()
    task = FollowUpTask(
        task="Integration smoke test follow-up",
        customer_email="john.doe@company.com",
        priority="low",
        status="open",
        category="general_information",
        description="Created by pytest integration smoke test.",
        source="pytest",
    )

    page_id = client.create_task(task)

    assert page_id
```

- [ ] **Step 2: Run normal Notion unit tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_notion_tasks_unit.py -v
```

Expected: unit tests pass; integration test passes if env vars are loaded into the test process and Notion is configured, otherwise skips.

- [ ] **Step 3: Commit integration smoke test**

Run:

```powershell
git add tests/test_notion_tasks_unit.py
git commit -m "test: add optional notion integration smoke test"
```

---

### Task 5: Update README

**Files:**
- Modify: `c03-t05-bruno-pieri-m1-challenge/README.md`

- [ ] **Step 1: Add Notion documentation**

Append this subsection under `## Week 3 - Advanced Memory and Tools MVP`:

```markdown
### Optional Notion Follow-up Integration

The follow-up increment can create tasks in a Notion database when a customer asks for
future action, such as:

```text
Pode criar um follow-up para verificar meu ticket amanhã?
```

Required `.env` values:

```env
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=37244176048e80dd8b66ee69bd1f36dc
```

The Notion database must include these properties:

| Property | Type |
|---|---|
| `Task` | Title |
| `Customer Email` | Email or Text |
| `Priority` | Select: `low`, `medium`, `high` |
| `Status` | Select: `open`, `in_progress`, `done` |
| `Category` | Select: `technical_support`, `billing`, `returns`, `product_inquiry`, `general_information` |
| `Due Date` | Date |
| `Description` | Text |
| `Source` | Text |

The core memory agent still works without Notion credentials. If a customer asks for a
follow-up and the credentials are missing or invalid, the agent keeps the service reply
and adds a short note that the Notion follow-up could not be created.
```

- [ ] **Step 2: Run README-neutral tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_followup_detector_unit.py tests/test_notion_tasks_unit.py tests/test_memory_agent_followup_unit.py -v
```

Expected: tests pass.

- [ ] **Step 3: Commit README update**

Run:

```powershell
git add README.md
git commit -m "docs: document notion followup integration"
```

---

### Task 6: Final Verification

**Files:**
- Read: `c03-t05-bruno-pieri-m1-challenge/README.md`
- Test: all Week 3 and Notion unit tests

- [ ] **Step 1: Run full unit and mandatory test suite**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_customer_tools_unit.py tests/test_hybrid_memory_unit.py tests/test_stop3.py tests/test_followup_detector_unit.py tests/test_notion_tasks_unit.py tests/test_memory_agent_followup_unit.py -v
```

Expected: all tests pass. The optional Notion integration test may pass or skip depending on whether `.env` variables are loaded into the test process.

- [ ] **Step 2: Run real Notion smoke test if credentials are available**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_notion_tasks_unit.py::test_create_task_against_real_notion_database -v
```

Expected: creates one page in the Notion database and passes. If environment variables are not loaded, it skips.

- [ ] **Step 3: Check git status**

Run:

```powershell
git status --short --branch
```

Expected: no uncommitted implementation changes in `c03-t05-bruno-pieri-m1-challenge`.

- [ ] **Step 4: Report result**

Report:

```text
Notion follow-up integration implemented.
Mandatory Week 3 tests still pass.
Notion smoke test: passed or skipped with reason.
```
