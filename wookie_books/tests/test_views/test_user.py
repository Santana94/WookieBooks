def test_create_user(client):
    response = client.post(
        "/users/",
        json={"username": "deadpool", "password": "chimichangas4life"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "deadpool"
    assert "id" in data


def test_get_user(base_user, client):
    response = client.get(f"/users/{base_user.id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == base_user.username
    assert data["id"] == base_user.id


def test_get_user_not_found(base_user, client):
    response = client.get(f"/users/{base_user.id + 10}/")
    assert response.status_code == 404


def test_list_users_with_books(base_users, client, create_base_books):
    users_data = [
        {"username": user.username, "id": user.id}
        for user in base_users
    ]
    for user_data in users_data:
        user_data["books"] = [
            {
                "author_id": user_book.author_id, "cover_image": user_book.cover_image,
                "description": user_book.description, "id": user_book.id, "price": user_book.price,
                "title": user_book.title
            }
            for user_book in create_base_books(user_id=user_data["id"])
        ]
    response = client.get(f"/users/")
    assert response.status_code == 200
    assert response.json() == users_data


def test_list_users_without_books(base_users, client):
    users_data = [
        {"username": user.username, "id": user.id, "books": []}
        for user in base_users
    ]
    response = client.get(f"/users/")
    assert response.status_code == 200
    assert response.json() == users_data


def test_list_no_users(client):
    response = client.get(f"/users/")
    assert response.status_code == 200
    assert response.json() == []
