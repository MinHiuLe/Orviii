import asyncio
from collections.abc import Awaitable, Callable

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

DB_CHECK_TIMEOUT_S = 2.0

DbCheck = Callable[[], Awaitable[None]]


def create_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True)


async def check_db(engine: AsyncEngine, timeout: float = DB_CHECK_TIMEOUT_S) -> None:
    """Run SELECT 1. Raises on failure or timeout."""
    async with asyncio.timeout(timeout):
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))


def get_db_check(request: Request) -> DbCheck:
    engine: AsyncEngine = request.app.state.engine

    async def _check() -> None:
        await check_db(engine)

    return _check
