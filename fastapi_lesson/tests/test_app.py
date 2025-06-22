from http import HTTPStatus


def test_root_deve_retornar_ok_hello_world(client) -> None:
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World!"}
