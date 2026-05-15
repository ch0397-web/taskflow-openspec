import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text
from dotenv import load_dotenv

load_dotenv()

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

_raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./taskflow.db").strip().lstrip("﻿")

IS_SQLITE = _raw_url.startswith("sqlite")


def _build_async_url(url: str) -> str:
    """Convert Neon/standard postgres URL to SQLAlchemy asyncpg URL, stripping unsupported params."""
    # SQLite: just fix driver prefix if needed, no param stripping required
    if url.startswith("sqlite"):
        if url.startswith("sqlite://") and not url.startswith("sqlite+"):
            return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url

    # PostgreSQL: fix driver prefix
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)

    # Strip parameters unsupported by asyncpg driver
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("channel_binding", None)  # not supported by asyncpg
    params.pop("sslmode", None)          # handled via connect_args below
    new_query = urlencode({k: v[0] for k, v in params.items()})
    return urlunparse(parsed._replace(query=new_query))


DATABASE_URL = _build_async_url(_raw_url)

connect_args = {}
if IS_SQLITE:
    connect_args = {"check_same_thread": False}
else:
    # asyncpg SSL for Neon (always required)
    connect_args = {"ssl": "require"}

engine = create_async_engine(DATABASE_URL, connect_args=connect_args, echo=False)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    from backend import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
