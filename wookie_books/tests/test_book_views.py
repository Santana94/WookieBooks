def test_read_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []


def test_darth_vader_can_not_create_book(client):
    response = client.post("/users/1/books/")
    assert response.status_code == 200
    assert response.json() == []
