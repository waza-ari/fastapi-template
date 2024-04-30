"""
Worker for background and cron tasks
"""

import asyncio
import logging.config
from typing import Any

import structlog
import uvloop

from app.core import FastAPIStructLogger, settings

from .db import DatabaseConnectionManager

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

log = FastAPIStructLogger()


def log_config() -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "arq.standard": {
                "level": "INFO",
                "class": "logging.NullHandler",
            }
        },
        "loggers": {"arq": {"handlers": ["arq.standard"], "level": "ERROR"}},
    }


async def startup(ctx: dict[Any, Any] | None) -> None:
    """
    Worker startup function
    """
    logging.config.dictConfig(log_config())
    ctx["dbmanager"] = DatabaseConnectionManager(settings.POSTGRES_URI, {"echo": False})
    await ctx["dbmanager"].connect()
    log.info("Worker Started")


async def shutdown(ctx: dict[Any, Any] | None) -> None:
    """
    Worker shutdown function
    """
    await ctx["dbmanager"].disconnect()
    log.info("Worker end")


async def on_job_start(ctx: dict[Any, Any] | None) -> None:
    """
    Job start
    """
    structlog.contextvars.bind_contextvars(job_id=ctx["job_id"])
    log.info("Job execution started")


async def on_job_complete(ctx: dict[Any, Any] | None) -> None:
    """
    Job complete
    """
    log.info("Job execution completed")
    structlog.contextvars.unbind_contextvars()
