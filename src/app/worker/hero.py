import asyncio
import uuid

from app.core.logger import FastAPIStructLogger
from app.crud import crud_hero

log = FastAPIStructLogger()


async def print_hero(ctx: dict[any, any] | None, hero_id: uuid.UUID) -> None:
    """
    Print hero by id
    """
    log.info(f"Printing hero {hero_id}")
    async with ctx["dbmanager"].session_scope() as db:
        hero = await crud_hero.get(db, hero_id)
        log.debug(f"Hero {hero_id} fetched", hero_name=hero.name)

    await asyncio.sleep(5)
    log.info(f"Hero {hero_id} printed")
