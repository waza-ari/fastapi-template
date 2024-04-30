from pydantic import BaseModel

from .mixins import SoftDeleteSchema, TimestampSchema, UUIDSchema, partial_model


class AbilityCreateSchema(BaseModel):
    name: str
    strength: int


class AbilitySchema(AbilityCreateSchema, UUIDSchema, TimestampSchema, SoftDeleteSchema):
    class Config:
        from_attributes = True


@partial_model
class AbilityUpdateSchema(AbilityCreateSchema):
    pass
