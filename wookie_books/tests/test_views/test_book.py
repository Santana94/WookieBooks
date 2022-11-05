import pytest


def test_list_no_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_books(client, create_base_books, base_user):
    user_id = base_user.id
    books = [
        {
            "author_id": user_book.author_id, "cover_image": user_book.cover_image,
            "description": user_book.description, "id": user_book.id, "price": user_book.price,
            "title": user_book.title
        }
        for user_book in create_base_books(user_id=user_id)
    ]
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == books


def test_unauthenticated_user_can_not_post_books(client):
    response = client.post("/users/1/books/")
    assert response.status_code == 401


@pytest.mark.parametrize("username", [
    "darth_somehting", "not_vader", "not_darth", "I am not vader", "Not DARTH HERE", "VaDeR", "darth_vader_official",
    "the_real_darth_vader"
])
def test_darth_vader_can_not_create_book(
    client, get_auth_headers, darth_vader, mocker, username, db, darth_vader_password
):
    darth_vader.username = username
    db.add(darth_vader)
    db.commit()
    mocker.patch("wookie_books.utils.write_file_to_media")
    headers = get_auth_headers(username=darth_vader.username, password=darth_vader_password)
    query_params = "?title=Title&description=Description&price=10000"
    with open("resources/Forests.jpg", "rb") as f:
        files = {"cover_image": ("filename", f, "image/jpeg")}
        response = client.post(
            f"/users/{darth_vader.id}/books/{query_params}", headers=headers, files=files
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "The dark lord can not submit books!"


def test_user_can_create_book(client, authenticate_user, base_user, mocker):
    mocker.patch("wookie_books.utils.write_file_to_media")
    author_id = base_user.id
    token_data = authenticate_user(username=base_user.username, password="generic")
    headers = {"Authorization": f"{token_data['token_type'].capitalize()} {token_data['access_token']}"}
    query_params = "?title=Title&description=Description&price=10000"
    with open("resources/Forests.jpg", "rb") as f:
        files = {"cover_image": ("filename", f, "image/jpeg")}
        response = client.post(
            f"/users/{base_user.id}/books/{query_params}", headers=headers, files=files
        )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop("id")
    assert response_data == {
        'title': 'Title', 'description': 'Description', 'price': 10000.0, 'author_id': author_id,
        'cover_image': 'media/filename'
    }
