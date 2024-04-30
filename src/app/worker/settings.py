"""
ARQ Worker settings
"""

from arq.connections import RedisSettings

from app.core import settings

from . import hero
from . import setup as fn

REDIS_QUEUE_HOST = settings.REDIS_QUEUE_HOST
REDIS_QUEUE_PORT = settings.REDIS_QUEUE_PORT


class WorkerSettings:
    """
    ARQ Worker settings
    """

    functions = [hero.print_hero]
    redis_settings = RedisSettings(host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT)
    on_startup = fn.startup
    on_shutdown = fn.shutdown
    on_job_start = fn.on_job_start
    after_job_end = fn.on_job_complete
    handle_signals = False
