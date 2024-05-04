"""
ARQ Worker settings
"""

from arq.connections import RedisSettings

from app.core import settings

from .hero import print_hero
from .setup import on_job_complete, on_job_start, shutdown, startup

REDIS_QUEUE_HOST = settings.REDIS_QUEUE_HOST
REDIS_QUEUE_PORT = settings.REDIS_QUEUE_PORT


class WorkerSettings:
    """
    ARQ Worker settings
    """

    functions = [print_hero]
    redis_settings = RedisSettings(host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT)
    on_startup = startup
    on_shutdown = shutdown
    on_job_start = on_job_start
    after_job_end = on_job_complete
