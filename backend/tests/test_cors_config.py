from fastapi.testclient import TestClient

from backend.app.core.config import get_settings
from backend.app.main import app


def test_cors_allows_frontend_origin():
    client = TestClient(app)
    origin = get_settings().frontend_origin

    response = client.options(
        "/api/auth/demo",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
