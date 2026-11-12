import logging

import structlog


def configure_logging() -> None:
    """Render every structlog event as one JSON line on stdout."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        # No cache_logger_on_first_use: it breaks structlog.testing.capture_logs.
    )
