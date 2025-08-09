import pytest
from backend import create_app
from backend.config import Config


@pytest.fixture
def client():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
