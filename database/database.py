from contextlib import asynccontextmanager

from environs import Env
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database.repository.user_repo import UserRepository


class Database:
    def __init__(self):
        env = Env()
        env.read_env('.env')

        self._url = URL.create(
            drivername='postgresql+asyncpg',
            username=env.str('POSTGRES_USER'),
            password=env.str('POSTGRES_PASSWORD'),
            host=env.str('POSTGRES_HOST'),
            database=env.str('POSTGRES_DB'),
            port=5432
        ).render_as_string(hide_password=False)

        self._engine = create_async_engine(
            self._url,
            echo=True
        )
        self._async_session_local = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def get_session(self):
        async with self._async_session_local() as session:
            yield session
