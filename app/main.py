from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.db import DbCheck, create_engine, get_db_check
from app.core.logging import configure_logging
from app.core.middleware import RequestIdMiddleware

configure_logging()
logger = structlog.get_logger("orviii.health")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_engine(get_settings().database_url)
    app.state.engine = engine
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)


@app.get("/health/live")
async def health_live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def health_ready(
    check: Annotated[DbCheck, Depends(get_db_check)],
) -> JSONResponse:
    try:
        await check()
    except Exception as exc:
        # Log only the exception class: messages may embed the connection string.
        logger.warning("readiness_check_failed", error_type=type(exc).__name__)
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return JSONResponse(content={"status": "ok"})
