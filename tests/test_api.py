from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert (
        "gemini_configured"
        in response.json()
    )


def test_generate_validation():

    response = client.post(
        "/generate",
        json={
            "document_type": "A"
        },
    )

    assert response.status_code == 422