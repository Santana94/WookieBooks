from fastapi.testclient import TestClient

from wookie_books.main import app

client = TestClient(app)


def test_read_books(test_db):
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []


def test_darth_vader_can_not_create_book(test_db):
    response = client.post("/users/1/books/")
    assert response.status_code == 200
    assert response.json() == []
