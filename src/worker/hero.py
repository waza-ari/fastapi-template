import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import FastAPIStructLogger
from app.crud import crud_hero

from .db import sessionmanager

log = FastAPIStructLogger()


async def print_hero(ctx: dict[any, any] | None, hero_id: uuid.UUID) -> None:
    """
    Print hero by id
    """
    log.info(f"Printing hero {hero_id}")

    db: AsyncSession = sessionmanager.scoped_session()

    hero = await crud_hero.get(db, hero_id)
    hero.name = ctx["job_id"]
    log.debug(f"Hero {hero_id} fetched", hero_name=hero.name)

    log.info(f"Hero {hero_id} printed")
