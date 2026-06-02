from fastapi.testclient import TestClient

from backend.app.core.config import get_settings
from backend.app.main import app


def test_demo_auth_accepts_correct_password(monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD", "demo-secret")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post("/api/auth/demo", json={"password": "demo-secret"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    get_settings.cache_clear()


def test_demo_auth_rejects_wrong_password(monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD", "demo-secret")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post("/api/auth/demo", json={"password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid demo password."
    get_settings.cache_clear()
