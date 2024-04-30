from app import models, schemas

from .base import CRUDBase

crud_ability = CRUDBase[models.Ability, schemas.AbilityCreateSchema, schemas.AbilityUpdateSchema](models.Ability)
