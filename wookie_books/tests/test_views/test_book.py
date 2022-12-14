import os

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


def test_get_book(client, create_book):
    base_book = create_book()
    book_data = {
        "author_id": base_book.author_id, "cover_image": base_book.cover_image,
        "description": base_book.description, "id": base_book.id, "price": base_book.price,
        "title": base_book.title
    }
    response = client.get(f"/books/{base_book.id}")
    assert response.status_code == 200
    assert response.json() == book_data


def test_get_no_book(client, create_book):
    base_book = create_book()
    response = client.get(f"/books/{base_book.id + 10}")
    assert response.status_code == 404


def test_delete_book(db, client, base_user, create_book, get_auth_headers, base_user_password):
    username = base_user.username
    book = create_book(user_id=base_user.id)
    book.cover_image = "resources/BookCover.jpg"
    db.add(book)
    db.commit()
    headers = get_auth_headers(username=username, password=base_user_password)
    with open(book.cover_image, "wb"):
        pass

    assert os.path.isfile(book.cover_image) is True

    response = client.delete(f"/books/{book.id}", headers=headers)
    assert response.status_code == 200
    assert os.path.isfile(book.cover_image) is False


def test_delete_book_not_authorized(client, create_book):
    base_book = create_book()
    response = client.delete(f"/books/{base_book.id}")
    assert response.status_code == 401


def test_delete_book_from_another_user(client, create_book, base_users, get_auth_headers, base_user_password):
    current_username = base_users[0].username
    base_book = create_book(user_id=base_users[1].id)
    headers = get_auth_headers(username=current_username, password=base_user_password)
    response = client.delete(f"/books/{base_book.id}", headers=headers)
    assert response.status_code == 401


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


def test_user_can_create_book(client, get_auth_headers, base_user, mocker):
    mocker.patch("wookie_books.utils.write_file_to_media")
    author_id = base_user.id
    headers = get_auth_headers(username=base_user.username, password="generic")
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
