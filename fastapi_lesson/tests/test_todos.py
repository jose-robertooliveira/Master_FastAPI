from http import HTTPStatus

import pytest

from fastapi_lesson.schemas import TodoFactory, TodoState

EXPECTED_TODOS = 5
EXPECTED_PAGINATED_TODOS = 2
NOT_FOUND_DETAIL = {"detail": "Task not found."}
SUCCESS_DELETE_MESSAGE = {"message": "Task has been deleted successfully."}


def create_todos(session, count, user_id, **kwargs):
    session.add_all(TodoFactory.create_batch(count, user_id=user_id, **kwargs))


def test_create_todo(client, token) -> None:
    payload = {
        "title": "Test todo",
        "description": "Test todo description",
        "state": "draft",
    }

    response = client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert response.json() == {"id": 1, **payload}


@pytest.mark.asyncio
async def test_list_todos(session, client, user, token) -> None:
    create_todos(session, EXPECTED_TODOS, user.id)
    await session.commit()

    response = client.get("/todos/", headers={"Authorization": f"Bearer {token}"})
    assert len(response.json()["todos"]) == EXPECTED_TODOS


@pytest.mark.asyncio
async def test_list_todos_pagination(session, client, user, token) -> None:
    create_todos(session, EXPECTED_TODOS, user.id)
    await session.commit()

    response = client.get(
        "/todos/?offset=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(response.json()["todos"]) == EXPECTED_PAGINATED_TODOS


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("filter_query", "factory_kwargs"),
    [
        (("title=Test todo 1"), {"title": "Test todo 1"}),
        (("description=desc"), {"description": "description"}),
        (("state=draft"), {"state": TodoState.draft}),
    ],
)
async def test_list_todos_filters(ctx, filter_query, factory_kwargs) -> None:
    session, client, user, token = (
        ctx["session"],
        ctx["client"],
        ctx["user"],
        ctx["token"],
    )

    create_todos(session, EXPECTED_TODOS, user.id, **factory_kwargs)
    await session.commit()

    response = client.get(
        f"/todos/?{filter_query}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(response.json()["todos"]) == EXPECTED_TODOS


@pytest.mark.asyncio
async def test_list_todos_combined_filters(session, client, user, token) -> None:
    create_todos(
        session,
        EXPECTED_TODOS,
        user.id,
        title="Test todo combined",
        description="combined description",
        state=TodoState.done,
    )
    create_todos(
        session,
        3,
        user.id,
        title="Other title",
        description="other description",
        state=TodoState.todo,
    )
    await session.commit()

    response = client.get(
        "/todos/?title=Test todo combined&description=combined&state=done",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(response.json()["todos"]) == EXPECTED_TODOS


@pytest.mark.asyncio
async def test_patch_todo(session, client, user, token) -> None:
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.patch(
        f"/todos/{todo.id}",
        json={"title": "updated"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == "updated"


def test_patch_todo_error(client, token) -> None:
    response = client.patch(
        "/todos/10",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == NOT_FOUND_DETAIL


@pytest.mark.asyncio
async def test_delete_todo(session, client, user, token) -> None:
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == SUCCESS_DELETE_MESSAGE


def test_delete_todo_error(client, token) -> None:
    response = client.delete(
        "/todos/10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == NOT_FOUND_DETAIL
