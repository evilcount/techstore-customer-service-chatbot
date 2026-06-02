from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.db.models import ChatMessage, ChatSession, utc_now


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, customer_email: str) -> ChatSession:
        session = ChatSession(customer_email=customer_email)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> ChatSession | None:
        return self.db.get(ChatSession, session_id)

    def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        message = ChatMessage(session_id=session_id, role=role, content=content)
        session = self.get_session(session_id)
        if session is not None:
            session.updated_at = utc_now()
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
