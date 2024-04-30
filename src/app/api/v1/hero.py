import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi_async_sqlalchemy import db

from app import models, schemas
from app.core import CrudEndpointCreator, FastAPIStructLogger, enqueue_job
from app.crud import crud_hero

router = APIRouter(prefix="/hero", tags=["heroes"])


# Demonstrate working with relationships
@router.get("/{hero_id}/ability", response_model=schemas.HeroSchema)
async def get_hero_ability(log: Annotated[FastAPIStructLogger, Depends()], hero_id: uuid.UUID):
    log.bind(requested_hero_id=hero_id)
    hero = await crud_hero.get(db.session, hero_id)
    if not hero:
        log.warning("Hero not found")
        raise HTTPException(status_code=404, detail="Hero not found")
    await db.session.refresh(hero, attribute_names=["ability"])
    log.info("Returning hero ability")
    await enqueue_job("print_hero", hero.id)
    await enqueue_job("print_hero", hero.id)
    return hero.ability


crud_generator = CrudEndpointCreator(
    crud=crud_hero,
    model=models.Hero,
    schema=schemas.HeroSchema,
    create_schema=schemas.HeroCreateSchema,
    update_schema=schemas.HeroUpdateSchema,
    filter_schema=schemas.HeroFilter,
)
crud_generator.add_routes_to_router(router)
