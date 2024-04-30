"""
Common mixins for Pydantic models.
"""

import uuid
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, create_model, field_serializer
from pydantic.fields import FieldInfo


# -------------- mixins --------------
class UUIDSchema:
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class TimestampSchema:
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, created_at: datetime | None, _info: Any) -> str | None:
        if created_at is not None:
            return created_at.isoformat()

        return None

    @field_serializer("updated_at")
    def serialize_updated_at(self, updated_at: datetime | None, _info: Any) -> str | None:
        if updated_at is not None:
            return updated_at.isoformat()

        return None


class SoftDeleteSchema:
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = False

    @field_serializer("deleted_at")
    def serialize_dates(self, deleted_at: datetime | None, _info: Any) -> str | None:
        if deleted_at is not None:
            return deleted_at.isoformat()

        return None


def partial_model(model: type[BaseModel]):
    def make_field_optional(field: FieldInfo, default: Any = None) -> tuple[Any, FieldInfo]:
        new = deepcopy(field)
        new.default = default
        new.annotation = field.annotation | None
        return new.annotation, new

    return create_model(
        f"Partial{model.__name__}",
        __base__=model,
        __module__=model.__module__,
        **{field_name: make_field_optional(field_info) for field_name, field_info in model.model_fields.items()},
    )
