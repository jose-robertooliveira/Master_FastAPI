from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_lesson.database import get_session
from fastapi_lesson.models import User
from fastapi_lesson.schemas import (
    FilterPage,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_lesson.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["users"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema, session: SessionDep) -> UserPublic:
    current_user = await session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if current_user:
        if current_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )
        elif current_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )

    current_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.get("/", status_code=HTTPStatus.OK)
async def read_users(
    session: SessionDep,
    filter_users: Annotated[FilterPage, Query()],
) -> UserList:
    users = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )

    return {"users": users}


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionDep,
    current_user: CurrentUser,
) -> UserPublic:
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions")

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Username or Email already exists"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions")
    await session.delete(current_user)
    await session.commit()

    return {"message": "User deleted"}
