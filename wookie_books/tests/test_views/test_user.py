import pytest


def test_create_user(client):
    response = client.post(
        "/users/",
        json={"username": "deadpool", "password": "chimichangas4life"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "deadpool"
    assert "id" in data


@pytest.mark.parametrize("data, error_field", [
    ({"username": "deadpool"}, "password"), ({"password": "chimichangas4life"}, "username")
])
def test_create_user_without_required_data(client, data, error_field):
    response = client.post(
        "/users/",
        json=data,
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [
        {
            'loc': ['body', error_field],
            'msg': 'field required',
            'type': 'value_error.missing'
        }
    ]}


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


@pytest.mark.parametrize("data, expected_response", [
    (
        {},
        {'books': [], 'username': 'base_user'},
    ),
    (
        {"username": "some_username"},
        {'books': [], 'username': 'some_username'},
    ),
    (
        {"password": "some_password"},
        {'books': [], 'username': 'base_user'},
    ),
    (
        {"password": "some_password", "username": "123"},
        {'books': [], 'username': '123'},
    ),
])
def test_update_user(
    base_user, client, data, expected_response, get_auth_headers, base_user_password
):
    headers = get_auth_headers(username=base_user.username, password=base_user_password)
    response = client.patch(f"/current_user/", json=data, headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.pop("id") == base_user.id
    assert response_data == expected_response


def test_update_user_with_no_permission(
    base_users, client, get_auth_headers, base_user_password
):
    response = client.patch(f"/current_user/", json={"password": "some_password", "username": "123"})
    assert response.status_code == 401
