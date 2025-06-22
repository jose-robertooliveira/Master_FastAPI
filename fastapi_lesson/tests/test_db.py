from dataclasses import asdict

import pytest
from sqlalchemy import select

# from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_lesson.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time) -> None:
    with mock_db_time(model=User) as time:
        new_user = User(username="iullia", email="iullia@example.com", password="secret")

        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == "iullia"))
    assert asdict(user) == {
        "id": 1,
        "username": "iullia",
        "email": "iullia@example.com",
        "password": "secret",
        "created_at": time,
        "todos": [],
    }
