from fastapi.testclient import TestClient

from wookie_books.main import app

client = TestClient(app)


def test_read_books():
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []
