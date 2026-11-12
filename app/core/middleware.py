import re
import time
import uuid

import structlog
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, clear_contextvars

# fullmatch (not "$") so a trailing newline cannot slip through.
_SAFE_ID = re.compile(r"[A-Za-z0-9-]{1,64}")

log = structlog.get_logger("orviii.access")


def pick_request_id(raw: str | None) -> str:
    if raw is not None and _SAFE_ID.fullmatch(raw):
        return raw
    return str(uuid.uuid4())


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw = None
        for name, value in scope["headers"]:
            if name == b"x-request-id":
                raw = value.decode("latin-1")
                break
        request_id = pick_request_id(raw)

        status = 500  # stays 500 if the app raises before sending a response
        start = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
            await send(message)

        bind_contextvars(request_id=request_id)
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            emit = log.error if status >= 500 else log.info
            # request_id is passed explicitly as well: capture_logs in tests
            # bypasses the contextvars processor.
            emit(
                "request",
                request_id=request_id,
                method=scope["method"],
                path=scope["path"],  # path only: no query string, headers or body
                status=status,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
            )
            clear_contextvars()
