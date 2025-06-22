from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_lesson.database import get_session
from fastapi_lesson.models import Todo, User
from fastapi_lesson.schemas import (
    FilterTodo,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fastapi_lesson.security import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/")
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: SessionDep,
) -> TodoPublic:
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get("/")
async def list_todos(
    session: SessionDep,
    user: CurrentUser,
    todo_filter: Annotated[FilterTodo, Query()],
) -> dict[str, list[Todo]]:
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(Todo.description.contains(todo_filter.description))

    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(query.offset(todo_filter.offset).limit(todo_filter.limit))

    return {"todos": todos.all()}


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, session: SessionDep, user: CurrentUser) -> dict[str, str]:
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found.")

    await session.delete(todo)
    await session.commit()

    return {"message": "Task has been deleted successfully."}


@router.patch("/{todo_id}")
async def patch_todo(
    todo_id: int, session: SessionDep, user: CurrentUser, todo: TodoUpdate
) -> TodoPublic:
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found.")

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
