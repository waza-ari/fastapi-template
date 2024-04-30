from app import models, schemas

from .base import CRUDBase

crud_hero = CRUDBase[models.Hero, schemas.HeroCreateSchema, schemas.HeroUpdateSchema](models.Hero)
