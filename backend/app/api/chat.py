from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.core.security import require_demo_password
from backend.app.db.repository import ChatRepository
from backend.app.db.session import get_db
from backend.app.services.chat_service import Agent, get_agent

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
    dependencies=[Depends(require_demo_password)],
)


class CreateSessionRequest(BaseModel):
    customer_email: EmailStr


class CreateSessionResponse(BaseModel):
    session_id: str
    customer_email: str


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    session_id: str
    assistant_message: str
    created_at: datetime


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ListMessagesResponse(BaseModel):
    messages: list[MessageResponse]


@router.post("/sessions", response_model=CreateSessionResponse)
def create_session(
    payload: CreateSessionRequest,
    db: Session = Depends(get_db),
) -> CreateSessionResponse:
    repo = ChatRepository(db)
    session = repo.create_session(str(payload.customer_email))
    return CreateSessionResponse(session_id=session.id, customer_email=session.customer_email)


@router.get("/sessions/{session_id}/messages", response_model=ListMessagesResponse)
def list_messages(
    session_id: str,
    db: Session = Depends(get_db),
) -> ListMessagesResponse:
    repo = ChatRepository(db)
    if repo.get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    messages = repo.list_messages(session_id)
    return ListMessagesResponse(
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in messages
        ]
    )


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
def send_message(
    session_id: str,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    agent: Agent = Depends(get_agent),
) -> SendMessageResponse:
    repo = ChatRepository(db)
    session = repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    repo.add_message(session_id, "user", user_message)
    assistant_message = agent.chat(session.customer_email, user_message)
    saved_reply = repo.add_message(session_id, "assistant", assistant_message)
    return SendMessageResponse(
        session_id=session_id,
        assistant_message=assistant_message,
        created_at=saved_reply.created_at,
    )
