from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.core.security import validate_demo_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class DemoAuthRequest(BaseModel):
    password: str


@router.post("/demo")
def demo_auth(payload: DemoAuthRequest) -> dict[str, bool]:
    validate_demo_password(payload.password)
    return {"ok": True}
