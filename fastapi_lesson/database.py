from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# from sqlalchemy.orm import sessionmaker
from fastapi_lesson.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)
# def get_engine(database_url: Optional[str] = None) -> AsyncEngine:  # pragma: no cover
#     url = database_url or Settings().DATABASE_URL
#     return create_async_engine(url)


# def get_session_maker(
#     engine: AsyncEngine,
# ) -> sessionmaker[AsyncSession]:  # pragma: no cover
#     return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# async def get_session() -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
#     engine = get_engine()
#     async_session = get_session_maker(engine)
#     async with async_session() as session:
#         yield session


async def get_session() -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
