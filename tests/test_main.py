from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_redirect():
    response = client.post("/links", json={"target_url": "https://example.com/page"})
    assert response.status_code == 201
    data = response.json()
    assert data["clicks"] == 0
    code = data["code"]
    assert len(code) == 7

    redirect = client.get(f"/{code}", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "https://example.com/page"

    stats = client.get(f"/links/{code}")
    assert stats.status_code == 200
    assert stats.json()["clicks"] == 1


def test_unknown_code_returns_404():
    response = client.get("/doesnotexist")
    assert response.status_code == 404
