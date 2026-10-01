from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "LegalEase API"

    assert data["status"] == "running"


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


def test_generate_validation():

    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "A",
            "terms": "B",
            "effective_date": "2026-04-10",
        },
    )

    assert response.status_code == 422