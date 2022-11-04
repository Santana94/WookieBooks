from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_create_user(test_db):
    response = client.post(
        "/users/",
        json={"username": "deadpool", "password": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "deadpool"
    assert "id" in data


# def test_list_user(generic_user):
#     response = client.get(f"/users/{generic_user.id}")
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["username"] == "deadpool"
#     assert data["id"] == generic_user.id
