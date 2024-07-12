from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "I'm up!"}
