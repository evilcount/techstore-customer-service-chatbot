from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.config import get_settings
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
    get_settings.cache_clear()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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


def teardown_overrides():
    app.dependency_overrides.clear()
    get_settings.cache_clear()


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
    teardown_overrides()


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
    teardown_overrides()


def test_chat_routes_require_demo_password(monkeypatch):
    client, _ = build_client(monkeypatch)

    response = client.post(
        "/api/chat/sessions",
        json={"customer_email": "john.doe@company.com"},
        headers={"X-Demo-Password": "wrong"},
    )

    assert response.status_code == 401
    teardown_overrides()
