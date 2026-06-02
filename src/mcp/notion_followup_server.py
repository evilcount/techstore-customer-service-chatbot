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
