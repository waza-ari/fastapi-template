from fastapi import APIRouter

from app import models, schemas
from app.core import CrudEndpointCreator
from app.crud import crud_ability

router = APIRouter(prefix="/ability", tags=["abilities"])

crud_generator = CrudEndpointCreator(
    crud=crud_ability,
    model=models.Ability,
    schema=schemas.AbilitySchema,
    create_schema=schemas.AbilityCreateSchema,
    update_schema=schemas.AbilityUpdateSchema,
)
crud_generator.add_routes_to_router(router)
