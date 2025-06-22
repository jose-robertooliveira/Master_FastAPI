from contextlib import contextmanager
from datetime import datetime
from typing import AsyncIterator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from fastapi_lesson.app import app
from fastapi_lesson.database import get_session
from fastapi_lesson.models import User, table_registry
from fastapi_lesson.schemas import UserFactory
from fastapi_lesson.security import get_password_hash
from fastapi_lesson.settings import Settings


@pytest.fixture(scope="session")
def engine():
    with PostgresContainer("postgres:17", driver="psycopg") as postgres:
        yield create_async_engine(postgres.get_connection_url())
        # yield _engine


@pytest_asyncio.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def client(session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_session] = lambda: session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def _create_user(session: AsyncSession, password: str) -> User:
    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    return user


@pytest_asyncio.fixture
async def user(session: AsyncSession) -> User:
    user = _create_user(session, "testtest")
    await session.commit()
    await session.refresh(user)
    user.clean_password = "testtest"
    return user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession) -> User:
    user = _create_user(session, "testtest")
    await session.commit()
    await session.refresh(user)
    user.clean_password = "testtest"
    return user


@pytest.fixture
def token(client, user) -> str:
    response = client.post(
        "/auth/token", data={"username": user.email, "password": user.clean_password}
    )
    return response.json()["access_token"]


@pytest.fixture
def settings() -> Settings:
    return Settings()


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 5, 29)) -> Generator[None, None, None]:
    def fake_time_hook(mapper, connection, target) -> None:
        if hasattr(target, "created_at"):
            target.created_at = time

    event.listen(model, "before_insert", fake_time_hook)
    yield time
    event.remove(model, "before_insert", fake_time_hook)


@pytest.fixture
def mock_db_time() -> Generator[None, None, None]:
    return _mock_db_time


@pytest.fixture
def ctx(session, client, user, token) -> dict[str, object]:
    return {
        "session": session,
        "client": client,
        "user": user,
        "token": token,
    }
