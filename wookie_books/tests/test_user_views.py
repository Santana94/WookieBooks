def test_create_user(client):
    response = client.post(
        "/users/",
        json={"username": "deadpool", "password": "chimichangas4life"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "deadpool"
    assert "id" in data


def test_list_user(base_user, client):
    response = client.get(f"/users/{base_user.id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == base_user.username
    assert data["id"] == base_user.id
