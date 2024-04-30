import datetime
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def _get(self, query_filter: Filter = None):
        sel = select(self.model)
        if query_filter:
            sel = query_filter.filter(sel)
            sel = query_filter.sort(sel)
        if hasattr(self.model, "deleted_at"):
            return sel.filter_by(deleted_at=None)
        return sel

    async def count(self, db: AsyncSession, query_filter=None) -> int:
        return (await db.scalar(self._get(query_filter))).count()

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        return await db.scalar(self._get().filter_by(id=id))

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        return await self.get(db, id) is not None

    async def get_deleted(self, db: AsyncSession, id: Any) -> ModelType | None:
        return await db.scalar(select(self.model).filter_by(id=id))

    async def get_paginated(self, db: AsyncSession, query_filter=None) -> Page[ModelType]:
        return await paginate(db, self._get(query_filter))

    async def get_multi(
        self, db: AsyncSession, query_filter: Filter = None, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        return (await db.scalars(self._get(query_filter).offset(skip).limit(limit))).all()

    async def get_all(self, db: AsyncSession, query_filter: Filter = None) -> Sequence[ModelType]:
        return (await db.scalars(self._get(query_filter))).all()

    async def get_all_deleted(self, db: AsyncSession, query_filter: Filter = None) -> Sequence[ModelType] | None:
        query = select(self.model)
        if query_filter:
            query = query_filter.filter(query)
            query = query_filter.sort(query)
        return (await db.scalars(query.filter(self.model.is_deleted.is_(True)))).all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, id: Any, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        # Fetch data first
        db_obj = await self.get(db, id)

        if not db_obj:
            raise ValueError("Model does not exist")

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def purge_all(self, db: AsyncSession) -> None:
        stmt = delete(self.model).where(self.model.is_deleted.is_(True))
        await db.execute(stmt)
        await db.commit()

    async def hard_delete(self, db: AsyncSession, id: Any) -> ModelType:
        obj = await self.get_deleted(db, id)
        if not obj:
            raise ValueError("Model does not exist")
        await db.delete(obj)
        await db.commit()
        return obj

    async def restore(self, db: AsyncSession, id: Any) -> ModelType:
        obj = await self.get_deleted(db, id)
        if not obj:
            raise ValueError("Model does not exist")
        if hasattr(obj, "deleted_at"):
            obj.deleted_at = None
            obj.is_deleted = False
            db.add(obj)
            await db.commit()
        else:
            raise ValueError("Model does not have deleted_at field")
        return obj

    async def delete(self, db: AsyncSession, id: Any) -> ModelType:
        obj = await self.get(db, id)
        if not obj:
            raise ValueError("Model does not exist")
        if hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.datetime.now()
            obj.is_deleted = True
            db.add(obj)
            await db.commit()
        else:
            await db.delete(obj)
            await db.commit()
        return obj
