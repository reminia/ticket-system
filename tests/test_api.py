from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "I'm up!"}


def test_create_ticket():
    response = client.post("/v1/ticket",
                           json={
                               "subject": "Ticket title",
                               "body": "Ticket body",
                               "customer_email": "user@example.com"
                           })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "submitted"
    assert "ticket_id" in data
    assert "message" in data


def test_get_ticket():
    response = client.post("/v1/ticket",
                           json={
                               "subject": "Ticket title",
                               "body": "Ticket body",
                               "customer_email": "user@example.com"
                           })
    ticket_id = response.json()["ticket_id"]
    query_response = client.get("/v1/ticket/%s" % ticket_id)
    assert query_response.status_code == 200


def test_get_non_exist_ticket():
    ticket_id = "9f091a6b-bc82-4413-b448-35be137884d0"
    response = client.get(f"/v1/ticket/{ticket_id}")
    assert response.status_code == 404
    assert 'detail' in response.json()
