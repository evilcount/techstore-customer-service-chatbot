from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from src.chains.memory_agent import MemoryAgent


class Agent(Protocol):
    def chat(self, customer_email: str, user_text: str) -> str:
        ...


@lru_cache
def get_agent() -> Agent:
    return MemoryAgent()
