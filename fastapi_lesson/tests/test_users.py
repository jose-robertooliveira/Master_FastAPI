from http import HTTPStatus

from fastapi_lesson.schemas import UserPublic


def test_create_user(client) -> None:
    response = client.post(
        "/users/",
        json={
            "username": "iullia",
            "email": "iullia@example.com",
            "password": "secret",
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "iullia",
        "email": "iullia@example.com",
        "id": 1,
    }


def test_read_users(client, user, token) -> None:
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_update_user(client, user, token) -> None:
    response = client.put(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "iullia",
            "email": "iullia@example.com",
            "password": "secret",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "iullia",
        "email": "iullia@example.com",
        "id": 1,
    }


def test_delete_user(client, user, token) -> None:
    response = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_update_integrity_error(client, user, token) -> None:
    client.post(
        "/users/",
        json={
            "username": "jonas",
            "email": "jonas@example.com",
            "password": "secret",
        },
    )
    response_update = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "jonas",
            "email": "jonas@example.com",
            "password": "secret",
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {"detail": "Username or Email already exists"}


def test_update_user_with_wrong_user(client, other_user, token) -> None:
    response = client.put(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "jonas",
            "email": "jonas@example.com",
            "password": "secret",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


def test_delete_user_wrong_user(client, other_user, token) -> None:
    response = client.delete(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}
