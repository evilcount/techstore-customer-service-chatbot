from __future__ import annotations

from fastapi import Header, HTTPException

from backend.app.core.config import get_settings


def validate_demo_password(password: str) -> None:
    if password != get_settings().demo_password:
        raise HTTPException(status_code=401, detail="Invalid demo password.")


def require_demo_password(x_demo_password: str = Header(default="")) -> None:
    validate_demo_password(x_demo_password)
