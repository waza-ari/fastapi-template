"""
Worker for background and cron tasks
"""

import asyncio
import logging.config
from typing import Any
from uuid import uuid4

import structlog
import uvloop
from arq.jobs import Job

from app.core import FastAPIStructLogger, settings, setup_logging

from .db import db_session_context, sessionmanager

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

log = FastAPIStructLogger()


def log_config() -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "arq": {"level": "WARNING"},
            "watchfiles.main": {"level": "WARNING"},
        },
    }


async def startup(ctx: dict[Any, Any] | None) -> None:
    """
    Worker startup function
    """
    logging.config.dictConfig(log_config())
    setup_logging(json_logs=settings.LOG_JSON_FORMAT, log_level=settings.LOG_LEVEL)
    await sessionmanager.connect()
    log.info("Worker Started")


async def shutdown(ctx: dict[Any, Any] | None) -> None:
    """
    Worker shutdown function
    """
    await sessionmanager.disconnect()
    log.info("Worker end")


async def on_job_start(ctx: dict[Any, Any] | None, cid: str | None = None) -> None:
    """
    Job start
    """
    db_session_context.set(ctx["job_id"])

    structlog.contextvars.bind_contextvars(job_id=ctx["job_id"])

    # Generate context id if not externally provided (created by FastAPI request)
    ctx["cid"] = ctx.get("cid", uuid4().hex)

    # Create DB session
    log.info("Job execution started")


async def on_job_complete(ctx: dict[Any, Any] | None) -> None:
    """
    Job complete
    """
    job_def = await Job(ctx["job_id"], ctx["redis"]).info()
    if hasattr(job_def, "success") and job_def.success:
        await sessionmanager.scoped_session().commit()
    else:
        await sessionmanager.scoped_session().rollback()

    # Close DB session
    await sessionmanager.scoped_session.remove()
    log.info("Job execution completed")
    structlog.contextvars.unbind_contextvars()
