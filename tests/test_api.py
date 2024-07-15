import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.database import get_db
from src.models.schemas import TicketStatus
from src.models.ticket import Ticket

client = TestClient(app)


@pytest.fixture
def mock_db_session(mocker):
    # Create a mock DB session
    return mocker.Mock()


@pytest.fixture(autouse=True)
def override_get_db(mock_db_session):
    # Override the get_db dependency to return the mock DB session
    app.dependency_overrides[get_db] = lambda: mock_db_session


@pytest.fixture
def mock_ticket():
    return Ticket(id=uuid.uuid4(),
                  subject="test",
                  body="test",
                  customer_email="test@email.com",
                  created_at=datetime.utcnow())


def test_root_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "I'm up!"}


def test_create_ticket(mocker):
    save_ticket = mocker.patch("src.api.v1.ticket_api.save_ticket")
    enqueue_ticket = mocker.patch("src.api.v1.ticket_api.enqueue_ticket")

    response = client.post("/v1/ticket",
                           json={
                               "subject": "Ticket title",
                               "body": "Ticket body",
                               "customer_email": "user@example.com"
                           })

    assert save_ticket.call_count == 1
    assert enqueue_ticket.call_count == 1
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "submitted"
    assert "ticket_id" in data
    assert "message" in data


def test_get_ticket(mocker, mock_ticket, mock_db_session):
    get_ticket = mocker.patch("src.api.v1.ticket_api.query_ticket")
    get_ticket.return_value = mock_ticket

    query_response = client.get("/v1/ticket/%s" % mock_ticket.id)
    assert query_response.status_code == 200
    get_ticket.assert_called_once_with(mock_db_session, mock_ticket.id)


def test_get_non_exist_ticket(mocker, mock_db_session):
    get_ticket = mocker.patch("src.api.v1.ticket_api.query_ticket")
    get_ticket.return_value = None

    ticket_id = uuid.uuid4()
    response = client.get(f"/v1/ticket/{str(ticket_id)}")

    assert response.status_code == 404
    assert 'detail' in response.json()


def test_process_ticket(mocker, mock_ticket, mock_db_session):
    mock_filter = mocker.patch("src.api.v1.ticket_api.filter_ticket_status")
    mock_filter.return_value = [mock_ticket, mock_ticket]

    mock_enqueue = mocker.patch("src.api.v1.ticket_api.enqueue_tickets")
    job_id = uuid.uuid4()
    mock_enqueue.return_value.id = job_id

    response = client.post("/v1/process")

    assert response.status_code == 200
    json = response.json()
    assert json['job_id'] == str(job_id)
    assert f"{len(mock_filter.return_value)} tickets" in json['message']
    mock_filter.assert_called_once_with(mock_db_session, TicketStatus.SUBMITTED)


def test_process_empty_ticket(mocker):
    mock_filter = mocker.patch("src.api.v1.ticket_api.filter_ticket_status")
    mock_filter.return_value = []

    response = client.post("/v1/process")

    assert mock_filter.call_count == 1
    assert response.status_code == 404
