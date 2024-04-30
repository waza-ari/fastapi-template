from arq.connections import ArqRedis, RedisSettings, create_pool
from asgi_correlation_id import correlation_id

pool: ArqRedis | None = None


async def create_redis_queue_pool(settings: RedisSettings) -> None:
    global pool
    pool = await create_pool(settings)


async def close_redis_queue_pool() -> None:
    global pool
    await pool.aclose()


async def enqueue_job(job_name: str, *args, **kwargs) -> None:
    """
    Enqueue a job in the Redis queue
    Automatically adds the correlation_id to the job

    :param job_name:
    :param args:
    :param kwargs:
    :return:
    """
    if pool is None:
        raise ValueError("Redis pool not initialized")

    await pool.enqueue_job(job_name, cid=correlation_id.get(), *args, **kwargs)
