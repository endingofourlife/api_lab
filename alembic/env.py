import asyncio
from logging.config import fileConfig

from environs import Env
from sqlalchemy import pool, URL
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from database.tables import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


env = Env()
env.read_env('.env')

url = URL.create(
    drivername='postgresql+asyncpg',
    username=env.str('POSTGRES_USER'),
    password=env.str('POSTGRES_PASSWORD'),
    host=env.str('POSTGRES_HOST'),
    database=env.str('POSTGRES_DB'),
    port=5432
).render_as_string(hide_password=False)

config.set_main_option(
    'sqlalchemy.url',
    url
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
