from __future__ import annotations

import os
from typing import Any

import requests

from src.components.followup_detector import FollowUpTask

NOTION_API_BASE_URL = "https://api.notion.com/v1"
NOTION_API_URL = f"{NOTION_API_BASE_URL}/pages"
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
        property_types: dict[str, str] | None = None,
    ) -> None:
        self.api_key = api_key
        self.database_id = database_id
        self._session = session or requests.Session()
        self._property_types = property_types

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
            "Customer Email": self._text_property("Customer Email", task.customer_email),
            "Priority": self._option_property("Priority", task.priority),
            "Status": self._option_property("Status", task.status),
            "Category": self._option_property("Category", task.category),
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
        self._ensure_property_types()
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

    def _ensure_property_types(self) -> None:
        if self._property_types is not None:
            return

        response = self._session.get(
            f"{NOTION_API_BASE_URL}/databases/{self.database_id}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": NOTION_VERSION,
            },
            timeout=30,
        )
        if response.status_code >= 400:
            raise NotionTaskError(
                f"Notion database schema lookup failed with {response.status_code}: {response.text}"
            )
        properties = response.json().get("properties", {})
        self._property_types = {
            name: str(config.get("type", ""))
            for name, config in properties.items()
            if isinstance(config, dict)
        }

    def _text_property(self, property_name: str, value: str) -> dict[str, Any]:
        property_type = self._property_type(property_name)
        if property_type == "multi_select":
            return {"multi_select": [{"name": value}]}
        if property_type == "rich_text":
            return {"rich_text": [{"text": {"content": value}}]}
        return {"email": value}

    def _option_property(self, property_name: str, value: str) -> dict[str, Any]:
        property_type = self._property_type(property_name)
        if property_type == "multi_select":
            return {"multi_select": [{"name": value}]}
        return {"select": {"name": value}}

    def _property_type(self, property_name: str) -> str:
        if self._property_types is None:
            return ""
        return self._property_types.get(property_name, "")
