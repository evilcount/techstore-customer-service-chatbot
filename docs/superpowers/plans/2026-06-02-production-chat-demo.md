# Production Chat Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deployable public demo with a Next.js chat frontend on Vercel, a FastAPI backend on Render, and PostgreSQL persistence for customer chat sessions and messages.

**Architecture:** Keep `src/` as the existing agent engine. Add `backend/` for FastAPI, auth, persistence, and agent orchestration, and `frontend/` for a customer-facing chat UI that calls the backend with a demo password.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy, PostgreSQL, pytest, Next.js, React, TypeScript, Vercel, Render.

---

## Files

- Create: `c03-t05-bruno-pieri-m1-challenge/backend/requirements.txt`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/main.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/api/auth.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/api/chat.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/core/config.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/core/security.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/db/session.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/db/models.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/db/repository.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/services/chat_service.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/tests/test_auth_api.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/tests/test_chat_api.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/package.json`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/next.config.js`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/tsconfig.json`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/app/page.tsx`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/app/globals.css`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/lib/api.ts`
- Modify: `c03-t05-bruno-pieri-m1-challenge/README.md`

---

### Task 1: Backend Project Skeleton and Health Endpoint

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/requirements.txt`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/main.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/tests/test_health_api.py`

- [ ] **Step 1: Write failing health endpoint test**

Create `backend/tests/test_health_api.py`:

```python
from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_health_api.py -v
```

Expected: fail with `ModuleNotFoundError` for `backend`.

- [ ] **Step 3: Add backend requirements**

Create `backend/requirements.txt`:

```text
fastapi
uvicorn[standard]
pydantic-settings
python-dotenv
sqlalchemy
psycopg[binary]
email-validator
pytest
httpx
```

- [ ] **Step 4: Implement FastAPI app**

Create `backend/app/__init__.py` as an empty file.

Create `backend/app/main.py`:

```python
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="TechStore Plus Chat API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 5: Install backend dependencies if needed**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

Expected: dependencies install successfully.

- [ ] **Step 6: Run test and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_health_api.py -v
```

Expected: test passes.

- [ ] **Step 7: Commit backend skeleton**

Run:

```powershell
git add backend/requirements.txt backend/app/__init__.py backend/app/main.py backend/tests/test_health_api.py
git commit -m "feat: add production api skeleton"
```

---

### Task 2: Configuration and Demo Password Auth

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/core/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/core/config.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/core/security.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/api/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/api/auth.py`
- Modify: `c03-t05-bruno-pieri-m1-challenge/backend/app/main.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/tests/test_auth_api.py`

- [ ] **Step 1: Write failing auth tests**

Create `backend/tests/test_auth_api.py`:

```python
from fastapi.testclient import TestClient

from backend.app.main import app


def test_demo_auth_accepts_correct_password(monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD", "demo-secret")
    client = TestClient(app)

    response = client.post("/api/auth/demo", json={"password": "demo-secret"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_demo_auth_rejects_wrong_password(monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD", "demo-secret")
    client = TestClient(app)

    response = client.post("/api/auth/demo", json={"password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid demo password."
```

- [ ] **Step 2: Run auth tests and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_auth_api.py -v
```

Expected: fail because `/api/auth/demo` does not exist.

- [ ] **Step 3: Implement settings**

Create `backend/app/core/__init__.py` as an empty file.

Create `backend/app/core/config.py`:

```python
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    demo_password: str = "demo"
    frontend_origin: str = "http://localhost:3000"
    database_url: str = "sqlite:///./chat_demo.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 4: Implement password validation helper**

Create `backend/app/core/security.py`:

```python
from __future__ import annotations

from fastapi import Header, HTTPException

from backend.app.core.config import get_settings


def validate_demo_password(password: str) -> None:
    if password != get_settings().demo_password:
        raise HTTPException(status_code=401, detail="Invalid demo password.")


def require_demo_password(x_demo_password: str = Header(default="")) -> None:
    validate_demo_password(x_demo_password)
```

- [ ] **Step 5: Implement auth router**

Create `backend/app/api/__init__.py` as an empty file.

Create `backend/app/api/auth.py`:

```python
from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from backend.app.core.security import validate_demo_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class DemoAuthRequest(BaseModel):
    password: str


@router.post("/demo")
def demo_auth(payload: DemoAuthRequest) -> dict[str, bool]:
    validate_demo_password(payload.password)
    return {"ok": True}
```

- [ ] **Step 6: Include auth router**

Update `backend/app/main.py`:

```python
from __future__ import annotations

from fastapi import FastAPI

from backend.app.api.auth import router as auth_router

app = FastAPI(title="TechStore Plus Chat API")
app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 7: Run auth tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_auth_api.py backend/tests/test_health_api.py -v
```

Expected: tests pass.

- [ ] **Step 8: Commit auth**

Run:

```powershell
git add backend/app/core backend/app/api backend/app/main.py backend/tests/test_auth_api.py
git commit -m "feat: add demo password auth"
```

---

### Task 3: Database Models and Repository

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/db/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/db/models.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/db/session.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/db/repository.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/tests/test_chat_repository.py`

- [ ] **Step 1: Write failing repository tests**

Create `backend/tests/test_chat_repository.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.models import Base
from backend.app.db.repository import ChatRepository


def make_repository():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return ChatRepository(session_factory())


def test_create_session_for_unknown_email():
    repo = make_repository()

    session = repo.create_session("new.customer@example.com")

    assert session.customer_email == "new.customer@example.com"
    assert session.id


def test_add_and_list_messages():
    repo = make_repository()
    session = repo.create_session("john.doe@company.com")

    repo.add_message(session.id, "user", "Hello")
    repo.add_message(session.id, "assistant", "Hi there")
    messages = repo.list_messages(session.id)

    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == ["Hello", "Hi there"]
```

- [ ] **Step 2: Run repository tests and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_chat_repository.py -v
```

Expected: fail because `backend.app.db` does not exist.

- [ ] **Step 3: Implement SQLAlchemy models**

Create `backend/app/db/__init__.py` as an empty file.

Create `backend/app/db/models.py`:

```python
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid4()))
    customer_email: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    session: Mapped[ChatSession] = relationship(back_populates="messages")
```

- [ ] **Step 4: Implement database session helper**

Create `backend/app/db/session.py`:

```python
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings
from backend.app.db.models import Base


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


engine = create_engine(normalize_database_url(get_settings().database_url))
SessionLocal = sessionmaker(bind=engine)


def create_tables() -> None:
    Base.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Implement repository**

Create `backend/app/db/repository.py`:

```python
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
```

- [ ] **Step 6: Run repository tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_chat_repository.py -v
```

Expected: tests pass.

- [ ] **Step 7: Commit database layer**

Run:

```powershell
git add backend/app/db backend/tests/test_chat_repository.py
git commit -m "feat: add chat persistence layer"
```

---

### Task 4: Chat API with Fake Agent Test

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/services/__init__.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/services/chat_service.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/app/api/chat.py`
- Modify: `c03-t05-bruno-pieri-m1-challenge/backend/app/main.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/tests/test_chat_api.py`

- [ ] **Step 1: Write failing chat API tests**

Create `backend/tests/test_chat_api.py`:

```python
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.models import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.services.chat_service import get_agent


class FakeAgent:
    def __init__(self):
        self.calls = []

    def chat(self, customer_email: str, user_text: str) -> str:
        self.calls.append((customer_email, user_text))
        return f"Reply to {customer_email}: {user_text}"


def build_client(monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD", "demo-secret")
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    fake_agent = FakeAgent()

    def override_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_agent] = lambda: fake_agent
    return TestClient(app), fake_agent


def test_create_session_accepts_unknown_email(monkeypatch):
    client, _ = build_client(monkeypatch)

    response = client.post(
        "/api/chat/sessions",
        json={"customer_email": "new.customer@example.com"},
        headers={"X-Demo-Password": "demo-secret"},
    )

    assert response.status_code == 200
    assert response.json()["customer_email"] == "new.customer@example.com"
    assert response.json()["session_id"]


def test_message_endpoint_persists_user_and_assistant_messages(monkeypatch):
    client, fake_agent = build_client(monkeypatch)
    session_response = client.post(
        "/api/chat/sessions",
        json={"customer_email": "john.doe@company.com"},
        headers={"X-Demo-Password": "demo-secret"},
    )
    session_id = session_response.json()["session_id"]

    response = client.post(
        f"/api/chat/sessions/{session_id}/messages",
        json={"message": "Hello"},
        headers={"X-Demo-Password": "demo-secret"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"] == "Reply to john.doe@company.com: Hello"
    assert fake_agent.calls == [("john.doe@company.com", "Hello")]

    messages_response = client.get(
        f"/api/chat/sessions/{session_id}/messages",
        headers={"X-Demo-Password": "demo-secret"},
    )
    messages = messages_response.json()["messages"]
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert [message["content"] for message in messages] == [
        "Hello",
        "Reply to john.doe@company.com: Hello",
    ]


def test_chat_routes_require_demo_password(monkeypatch):
    client, _ = build_client(monkeypatch)

    response = client.post(
        "/api/chat/sessions",
        json={"customer_email": "john.doe@company.com"},
        headers={"X-Demo-Password": "wrong"},
    )

    assert response.status_code == 401
```

- [ ] **Step 2: Run chat API tests and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_chat_api.py -v
```

Expected: fail because chat API modules do not exist.

- [ ] **Step 3: Implement chat service**

Create `backend/app/services/__init__.py` as an empty file.

Create `backend/app/services/chat_service.py`:

```python
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
```

- [ ] **Step 4: Implement chat router**

Create `backend/app/api/chat.py`:

```python
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
    return ListMessagesResponse(messages=repo.list_messages(session_id))


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

    repo.add_message(session_id, "user", payload.message)
    assistant_message = agent.chat(session.customer_email, payload.message)
    saved_reply = repo.add_message(session_id, "assistant", assistant_message)
    return SendMessageResponse(
        session_id=session_id,
        assistant_message=assistant_message,
        created_at=saved_reply.created_at,
    )
```

- [ ] **Step 5: Include chat router and create tables on startup**

Update `backend/app/main.py`:

```python
from __future__ import annotations

from fastapi import FastAPI

from backend.app.api.auth import router as auth_router
from backend.app.api.chat import router as chat_router
from backend.app.db.session import create_tables

app = FastAPI(title="TechStore Plus Chat API")
app.include_router(auth_router)
app.include_router(chat_router)


@app.on_event("startup")
def startup() -> None:
    create_tables()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 6: Run chat API tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_chat_api.py -v
```

Expected: tests pass.

- [ ] **Step 7: Commit chat API**

Run:

```powershell
git add backend/app/api/chat.py backend/app/main.py backend/app/services backend/tests/test_chat_api.py
git commit -m "feat: add persisted chat api"
```

---

### Task 5: CORS and Local API Run Verification

**Files:**
- Modify: `c03-t05-bruno-pieri-m1-challenge/backend/app/main.py`
- Create: `c03-t05-bruno-pieri-m1-challenge/backend/tests/test_cors_config.py`

- [ ] **Step 1: Write failing CORS test**

Create `backend/tests/test_cors_config.py`:

```python
from fastapi.testclient import TestClient

from backend.app.main import app


def test_cors_allows_frontend_origin(monkeypatch):
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:3000")
    client = TestClient(app)

    response = client.options(
        "/api/auth/demo",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
```

- [ ] **Step 2: Run CORS test and verify RED**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests/test_cors_config.py -v
```

Expected: fail because CORS middleware is not configured.

- [ ] **Step 3: Add CORS middleware**

Update `backend/app/main.py`:

```python
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.auth import router as auth_router
from backend.app.api.chat import router as chat_router
from backend.app.core.config import get_settings
from backend.app.db.session import create_tables

settings = get_settings()
app = FastAPI(title="TechStore Plus Chat API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(chat_router)


@app.on_event("startup")
def startup() -> None:
    create_tables()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Run backend tests and verify GREEN**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests -v
```

Expected: backend tests pass.

- [ ] **Step 5: Commit CORS**

Run:

```powershell
git add backend/app/main.py backend/tests/test_cors_config.py
git commit -m "feat: configure api cors"
```

---

### Task 6: Frontend Next.js Skeleton and API Client

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/package.json`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/next.config.js`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/tsconfig.json`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/app/layout.tsx`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/app/globals.css`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/lib/api.ts`

- [ ] **Step 1: Create frontend package**

Create `frontend/package.json`:

```json
{
  "name": "techstore-chat-demo",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "vitest run"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.0.0",
    "@vitejs/plugin-react": "^5.0.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "jsdom": "^25.0.0",
    "typescript": "^5.6.0",
    "vitest": "^3.0.0"
  }
}
```

- [ ] **Step 2: Create Next config**

Create `frontend/next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {};

module.exports = nextConfig;
```

- [ ] **Step 3: Create TypeScript config**

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 4: Create app layout**

Create `frontend/app/layout.tsx`:

```tsx
import "./globals.css";

export const metadata = {
  title: "TechStore Plus Support",
  description: "Customer support chat demo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 5: Create API helper**

Create `frontend/lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {},
  demoPassword?: string,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(demoPassword ? { "X-Demo-Password": demoPassword } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export function validateDemoPassword(password: string) {
  return request<{ ok: boolean }>("/api/auth/demo", {
    method: "POST",
    body: JSON.stringify({ password }),
  });
}

export function createSession(customerEmail: string, demoPassword: string) {
  return request<{ session_id: string; customer_email: string }>(
    "/api/chat/sessions",
    {
      method: "POST",
      body: JSON.stringify({ customer_email: customerEmail }),
    },
    demoPassword,
  );
}

export function sendMessage(sessionId: string, message: string, demoPassword: string) {
  return request<{ session_id: string; assistant_message: string; created_at: string }>(
    `/api/chat/sessions/${sessionId}/messages`,
    {
      method: "POST",
      body: JSON.stringify({ message }),
    },
    demoPassword,
  );
}
```

- [ ] **Step 6: Create basic CSS**

Create `frontend/app/globals.css`:

```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  background: #f6f7fb;
  color: #1f2937;
}

button,
input {
  font: inherit;
}
```

- [ ] **Step 7: Install frontend dependencies**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge\frontend
npm install
```

Expected: dependencies install and `package-lock.json` is created.

- [ ] **Step 8: Run frontend build baseline**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge\frontend
npm run build
```

Expected: build may fail because `app/page.tsx` is not created yet. This is acceptable at this task boundary.

- [ ] **Step 9: Commit frontend skeleton**

Run:

```powershell
git add frontend
git commit -m "feat: add next chat frontend skeleton"
```

---

### Task 7: Frontend Chat UI

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/app/page.tsx`
- Modify: `c03-t05-bruno-pieri-m1-challenge/frontend/app/globals.css`

- [ ] **Step 1: Create chat page**

Create `frontend/app/page.tsx`:

```tsx
"use client";

import { FormEvent, useState } from "react";
import { createSession, sendMessage, validateDemoPassword } from "../lib/api";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

const demoEmails = [
  "john.doe@company.com",
  "sarah.smith@company.com",
  "emily.brown@company.com",
];

export default function Home() {
  const [demoPassword, setDemoPassword] = useState("");
  const [isAuthed, setIsAuthed] = useState(false);
  const [customerEmail, setCustomerEmail] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handlePasswordSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await validateDemoPassword(demoPassword);
      setIsAuthed(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid password");
    }
  }

  async function ensureSession() {
    if (sessionId) {
      return sessionId;
    }
    const session = await createSession(customerEmail, demoPassword);
    setSessionId(session.session_id);
    return session.session_id;
  }

  async function handleMessageSubmit(event: FormEvent) {
    event.preventDefault();
    if (!customerEmail || !message.trim()) {
      return;
    }

    const userMessage = message.trim();
    setMessage("");
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setIsLoading(true);
    setError("");

    try {
      const activeSessionId = await ensureSession();
      const response = await sendMessage(activeSessionId, userMessage, demoPassword);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.assistant_message },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send message");
    } finally {
      setIsLoading(false);
    }
  }

  if (!isAuthed) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <p className="eyebrow">TechStore Plus</p>
          <h1>Support Chat Demo</h1>
          <form onSubmit={handlePasswordSubmit}>
            <label htmlFor="password">Demo password</label>
            <input
              id="password"
              type="password"
              value={demoPassword}
              onChange={(event) => setDemoPassword(event.target.value)}
              placeholder="Enter demo password"
            />
            <button type="submit">Enter demo</button>
          </form>
          {error ? <p className="error">{error}</p> : null}
        </section>
      </main>
    );
  }

  return (
    <main className="chat-shell">
      <section className="sidebar">
        <p className="eyebrow">TechStore Plus</p>
        <h1>Support</h1>
        <label htmlFor="email">Customer email</label>
        <input
          id="email"
          value={customerEmail}
          onChange={(event) => {
            setCustomerEmail(event.target.value);
            setSessionId(null);
            setMessages([]);
          }}
          placeholder="new.customer@example.com"
        />
        <div className="demo-list">
          {demoEmails.map((email) => (
            <button
              key={email}
              type="button"
              onClick={() => {
                setCustomerEmail(email);
                setSessionId(null);
                setMessages([]);
              }}
            >
              {email}
            </button>
          ))}
        </div>
      </section>

      <section className="chat-panel">
        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              Enter any customer email and start a support conversation.
            </div>
          ) : (
            messages.map((chatMessage, index) => (
              <div key={index} className={`bubble ${chatMessage.role}`}>
                {chatMessage.content}
              </div>
            ))
          )}
          {isLoading ? <div className="bubble assistant">Agent is typing...</div> : null}
        </div>

        <form className="composer" onSubmit={handleMessageSubmit}>
          <input
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Type your message..."
            disabled={!customerEmail || isLoading}
          />
          <button type="submit" disabled={!customerEmail || !message.trim() || isLoading}>
            Send
          </button>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </section>
    </main>
  );
}
```

- [ ] **Step 2: Replace CSS with chat layout**

Replace `frontend/app/globals.css` with:

```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  background: #f6f7fb;
  color: #1f2937;
}

button,
input {
  font: inherit;
}

.auth-shell,
.chat-shell {
  min-height: 100vh;
}

.auth-shell {
  display: grid;
  place-items: center;
  padding: 24px;
}

.auth-panel {
  width: min(420px, 100%);
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 28px;
}

.auth-panel form,
.sidebar,
.composer {
  display: grid;
  gap: 12px;
}

.eyebrow {
  margin: 0;
  color: #2563eb;
  font-weight: 700;
  font-size: 13px;
  text-transform: uppercase;
}

h1 {
  margin: 8px 0 20px;
}

label {
  font-weight: 700;
}

input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 12px;
  width: 100%;
}

button {
  border: 0;
  border-radius: 8px;
  padding: 12px 14px;
  background: #2563eb;
  color: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.chat-shell {
  display: grid;
  grid-template-columns: 320px 1fr;
}

.sidebar {
  background: white;
  border-right: 1px solid #e5e7eb;
  padding: 24px;
  align-content: start;
}

.demo-list {
  display: grid;
  gap: 8px;
}

.demo-list button {
  background: #eef2ff;
  color: #1e40af;
  text-align: left;
}

.chat-panel {
  display: grid;
  grid-template-rows: 1fr auto;
  min-height: 100vh;
  padding: 24px;
}

.messages {
  align-content: end;
  display: grid;
  gap: 12px;
  overflow-y: auto;
  padding-bottom: 20px;
}

.empty-state {
  color: #6b7280;
  text-align: center;
}

.bubble {
  border-radius: 8px;
  max-width: 760px;
  padding: 12px 14px;
  white-space: pre-wrap;
}

.bubble.user {
  justify-self: end;
  background: #2563eb;
  color: white;
}

.bubble.assistant {
  justify-self: start;
  background: white;
  border: 1px solid #e5e7eb;
}

.composer {
  grid-template-columns: 1fr auto;
}

.error {
  color: #b91c1c;
}

@media (max-width: 800px) {
  .chat-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: 0;
    border-bottom: 1px solid #e5e7eb;
  }
}
```

- [ ] **Step 3: Run frontend build**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge\frontend
npm run build
```

Expected: build passes.

- [ ] **Step 4: Commit chat UI**

Run:

```powershell
git add frontend
git commit -m "feat: add production chat frontend"
```

---

### Task 8: Frontend Rendering Tests

**Files:**
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/vitest.config.ts`
- Create: `c03-t05-bruno-pieri-m1-challenge/frontend/tests/chat-page.test.tsx`
- Modify: `c03-t05-bruno-pieri-m1-challenge/frontend/package.json`

- [ ] **Step 1: Add Vitest config**

Create `frontend/vitest.config.ts`:

```typescript
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
  },
});
```

- [ ] **Step 2: Write frontend rendering tests**

Create `frontend/tests/chat-page.test.tsx`:

```tsx
import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Home from "../app/page";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("TechStore chat page", () => {
  it("renders the demo password screen first", () => {
    render(<Home />);

    expect(screen.getByText("Support Chat Demo")).toBeInTheDocument();
    expect(screen.getByLabelText("Demo password")).toBeInTheDocument();
  });

  it("shows customer email input after valid demo password", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ok: true }),
    } as Response);

    render(<Home />);
    fireEvent.change(screen.getByLabelText("Demo password"), {
      target: { value: "demo" },
    });
    fireEvent.click(screen.getByText("Enter demo"));

    await waitFor(() => {
      expect(screen.getByLabelText("Customer email")).toBeInTheDocument();
    });
    expect(screen.getByText("Enter any customer email and start a support conversation.")).toBeInTheDocument();
  });

  it("allows a new customer email before sending a message", async () => {
    vi.spyOn(global, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          session_id: "session-1",
          customer_email: "new.customer@example.com",
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          session_id: "session-1",
          assistant_message: "Hello new customer",
          created_at: "2026-06-02T00:00:00Z",
        }),
      } as Response);

    render(<Home />);
    fireEvent.change(screen.getByLabelText("Demo password"), {
      target: { value: "demo" },
    });
    fireEvent.click(screen.getByText("Enter demo"));

    await screen.findByLabelText("Customer email");
    fireEvent.change(screen.getByLabelText("Customer email"), {
      target: { value: "new.customer@example.com" },
    });
    fireEvent.change(screen.getByPlaceholderText("Type your message..."), {
      target: { value: "Hi" },
    });
    fireEvent.click(screen.getByText("Send"));

    await waitFor(() => {
      expect(screen.getByText("Hello new customer")).toBeInTheDocument();
    });
  });
});
```

- [ ] **Step 3: Run frontend tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge\frontend
npm test
```

Expected: all frontend tests pass.

- [ ] **Step 4: Commit frontend tests**

Run:

```powershell
git add frontend/vitest.config.ts frontend/tests/chat-page.test.tsx frontend/package.json
git commit -m "test: cover production chat frontend"
```

---

### Task 9: Deployment Documentation

**Files:**
- Modify: `c03-t05-bruno-pieri-m1-challenge/README.md`

- [ ] **Step 1: Add production deployment section**

Append to `README.md`:

```markdown
## Production Chat Demo

The production demo uses:

- FastAPI backend in `backend/`
- Next.js frontend in `frontend/`
- PostgreSQL for persisted chat sessions and messages

### Local Backend

```powershell
..\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
..\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Required backend `.env` values:

```env
OPENAI_API_KEY=...
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
DATABASE_URL=sqlite:///./chat_demo.db
DEMO_PASSWORD=demo
FRONTEND_ORIGIN=http://localhost:3000
```

### Local Frontend

```powershell
cd frontend
npm install
npm run dev
```

Required frontend `.env.local` value:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Render Backend

Create a Render Web Service from this repository.

- Root directory: `c03-t05-bruno-pieri-m1-challenge`
- Build command: `pip install -r backend/requirements.txt -r requirements.txt`
- Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Add Render PostgreSQL and set `DATABASE_URL` from the managed database connection string.

### Vercel Frontend

Create a Vercel project from this repository.

- Root directory: `c03-t05-bruno-pieri-m1-challenge/frontend`
- Framework preset: Next.js
- Environment variable: `NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com`

### Deployment Smoke Test

1. Open the Vercel URL.
2. Enter `DEMO_PASSWORD`.
3. Enter any email address.
4. Send `Hello, can you help me?`.
5. Confirm the assistant replies.
6. Send a follow-up request such as `Pode criar um follow-up para verificar meu ticket amanhã?`.
7. Confirm a task appears in Notion if Notion environment variables are configured.
```

- [ ] **Step 2: Commit deployment docs**

Run:

```powershell
git add README.md
git commit -m "docs: add production demo deployment guide"
```

---

### Task 10: Final Verification

**Files:**
- Test: backend and existing Week 3 tests
- Test: frontend tests and build

- [ ] **Step 1: Run backend tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest backend/tests -v
```

Expected: all backend tests pass.

- [ ] **Step 2: Run existing Week 3 tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
..\.venv\Scripts\python.exe -m pytest tests/test_customer_tools_unit.py tests/test_hybrid_memory_unit.py tests/test_stop3.py tests/test_followup_detector_unit.py tests/test_notion_tasks_unit.py tests/test_memory_agent_followup_unit.py tests/test_mcp_notion_followup_unit.py -v
```

Expected: all existing tests pass.

- [ ] **Step 3: Run frontend tests**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge\frontend
npm test
```

Expected: frontend tests pass.

- [ ] **Step 4: Run frontend build**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge\frontend
npm run build
```

Expected: Next.js production build succeeds.

- [ ] **Step 5: Check git status**

Run:

```powershell
cd c03-t05-bruno-pieri-m1-challenge
git status --short --branch
```

Expected: no uncommitted changes in the subproject.

- [ ] **Step 6: Report result**

Report:

```text
Production chat demo plan implemented.
Backend tests: passed.
Week 3 tests: passed.
Frontend tests: passed.
Frontend build: passed.
Deploy targets documented: Render backend, Render PostgreSQL, Vercel frontend.
```
