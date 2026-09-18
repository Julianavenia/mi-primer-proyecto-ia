from fastapi.testclient import TestClient

from mi_primer_proyecto_ia.api.main import app


def test_health_returns_ok_and_fake_backend():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["llm_backend"] == "fake"
