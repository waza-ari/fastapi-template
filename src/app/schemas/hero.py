import uuid

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel

from app.models import Hero

from .mixins import SoftDeleteSchema, TimestampSchema, UUIDSchema, partial_model


class HeroCreateSchema(BaseModel):
    name: str
    ability_id: uuid.UUID | None = None


class HeroSchema(HeroCreateSchema, UUIDSchema, TimestampSchema, SoftDeleteSchema):
    class Config:
        from_attributes = True


@partial_model
class HeroUpdateSchema(HeroCreateSchema):
    pass


class HeroFilter(Filter):
    name: str | None = None
    name__ilike: str | None = None
    name__like: str | None = None
    name__neq: str | None = None

    order_by: list[str] = ["name"]
    search: str | None = None

    class Constants(Filter.Constants):
        model = Hero
        search_model_fields = ["name"]
