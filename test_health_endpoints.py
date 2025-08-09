from backend import create_app
from backend.config import Config
import pytest


@pytest.fixture
def client():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_api_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["database"] in ["connected", "disconnected"]
