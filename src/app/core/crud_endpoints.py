import uuid
from collections.abc import Sequence
from enum import Enum
from inspect import Parameter, Signature
from typing import Annotated, TypeVar

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_async_sqlalchemy import db
from fastapi_filter import FilterDepends  # noqa  # Must be imported for makefun to work
from fastapi_pagination import Page
from makefun import with_signature
from pydantic import BaseModel

from app.crud.base import CRUDBase
from app.models.base import Base

from .logger import FastAPIStructLogger

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=BaseModel)


class CrudEndpointCreator:
    def __init__(
        self,
        crud: CRUDBase,
        model: type[ModelType],
        schema: type[SchemaType],
        create_schema: type[CreateSchemaType],
        update_schema: type[UpdateSchemaType],
        filter_schema: type[FilterSchemaType] | None = None,
    ):
        self.crud = crud
        self.model = model
        self.schema = schema
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.filter_schema = filter_schema

        # Construct endpoint parameter signatures for makefun depending on the presence of a filter schema
        self.parameters = [
            Parameter(
                "log",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[FastAPIStructLogger, Depends()],
            )
        ]
        if self.filter_schema:
            self.parameters.append(
                Parameter(
                    "filter",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=FilterSchemaType,
                    default=FilterDepends(self.filter_schema),
                )
            )

    def _read_item(self):
        """Creates an endpoint for reading a single item from the database."""

        async def endpoint(
            log: Annotated[FastAPIStructLogger, Depends()],
            id: uuid.UUID,
        ):
            log.bind(db_model=self.model.__name__, db_id=id)
            log.info("Reading a single database entry using CRUD read endpoint")
            item = await self.crud.get(db.session, id)
            if not item:  # pragma: no cover
                log.warning("Item not found in the database")
                raise HTTPException(status_code=404, detail="Item not found")
            log.info("Database entry read successfully")
            return item  # pragma: no cover

        return endpoint

    def _read_items(self):
        """Creates an endpoint for reading all items from the database."""

        @with_signature(
            Signature(self.parameters, return_annotation=Sequence[self.schema])
        )
        async def endpoint(*args, **kwargs):
            log = kwargs.get("log")
            log.bind(db_model=self.model.__name__)
            log.info("Reading all database entries using CRUD read endpoint")
            items = await self.crud.get_all(db.session, kwargs.get("filter") or None)
            log.bind(found_items=len(items))
            log.info("Database entries read successfully")
            return items  # pragma: no cover

        return endpoint

    def _read_deleted(self):
        """
        Creates an endpoint for reading all deleted items from the database.
        """

        @with_signature(
            Signature(self.parameters, return_annotation=Sequence[self.schema])
        )
        async def endpoint(*args, **kwargs):
            log = kwargs.get("log")
            log.bind(db_model=self.model.__name__)
            log.info("Reading all deleted database entries using CRUD read endpoint")
            items = await self.crud.get_all_deleted(
                db.session, kwargs.get("filter") or None
            )
            log.bind(found_items=len(items))
            log.info("Database entries read successfully")
            return items  # pragma: no cover

        return endpoint

    def _read_paginated(self):
        """Creates an endpoint for reading multiple items from the database with pagination."""

        @with_signature(
            func_signature=Signature(
                self.parameters, return_annotation=Page[self.schema]
            ),
            func_name="read_paginated",
        )
        async def endpoint(*args, **kwargs):
            log = kwargs.get("log")
            log.bind(db_model=self.model.__name__)
            log.info("Reading multiple database entries using CRUD read endpoint")
            return await self.crud.get_paginated(
                db.session, kwargs.get("filter") or None
            )

        return endpoint

    def _create_item(self):
        """Creates an endpoint for creating items in the database."""

        async def endpoint(
            log: Annotated[FastAPIStructLogger, Depends()],
            item: self.create_schema = Body(...),
        ) -> self.schema:
            log.bind(db_model=self.model.__name__)
            log.info("Creating a new database entry using CRUD create endpoint")
            log.debug("Data has been passed to the endpoint", data=item.dict())
            result = await self.crud.create(db.session, item)
            log.bind(db_id=str(result.id))
            log.info("Database entry created successfully")
            return result

        return endpoint

    def _update_item(self):
        """Creates an endpoint for updating an existing item in the database."""

        async def endpoint(
            log: Annotated[FastAPIStructLogger, Depends()],
            id: uuid.UUID,
            item: self.update_schema = Body(...),
        ):
            log.bind(db_model=self.model.__name__, db_id=id)
            log.info("Updating a database entry using CRUD update endpoint")
            log.debug("Data has been passed to the endpoint", data=item.dict())
            # Verify existence of the item
            item_exists = await self.crud.exists(db.session, id)
            if not item_exists:  # pragma: no cover
                log.warning("Item not found in the database")
                raise HTTPException(status_code=404, detail="Item not found")
            updated_entry = await self.crud.update(db.session, id, item)
            log.info("Database entry updated successfully")
            return updated_entry

        return endpoint

    def _delete_item(self):
        """Creates an endpoint for deleting an item from the database."""

        async def endpoint(
            log: Annotated[FastAPIStructLogger, Depends()],
            id: uuid.UUID,
        ):
            log.bind(db_model=self.model.__name__, db_id=id)
            log.info("Deleting a database entry using CRUD delete endpoint")
            await self.crud.delete(db.session, id)
            log.info("Database entry deleted successfully")
            return {"message": "Item deleted successfully"}  # pragma: no cover

        return endpoint

    def _restore_item(self):
        """
        Creates an endpoint for restoring a soft-deleted item in the database.
        """

        async def endpoint(
            log: Annotated[FastAPIStructLogger, Depends()],
            id: uuid.UUID,
        ):
            log.bind(db_model=self.model.__name__, db_id=id)
            log.info("Restoring a database entry")
            try:
                entry = await self.crud.restore(db.session, id)
                log.info("Database entry restored successfully")
                return entry
            except ValueError as e:  # pragma: no cover
                log.warning("Error restoring database entry")
                raise HTTPException(status_code=404, detail=str(e))

        return endpoint

    def _purge_item(self):
        """
        Creates an endpoint for purging a soft-deleted item from the database.
        """

        async def endpoint(
            log: Annotated[FastAPIStructLogger, Depends()],
            id: uuid.UUID,
        ):
            log.bind(db_model=self.model.__name__, db_id=id)
            log.info("Purging a soft-deleted database entry")
            try:
                entry = await self.crud.hard_delete(db.session, id)
                log.info("Database entry purged successfully")
                return entry
            except ValueError as e:  # pragma: no cover
                log.warning("Error purging database entry")
                raise HTTPException(status_code=404, detail=str(e))

        return endpoint

    def _purge_all(self):
        """
        Creates an endpoint for purging a soft-deleted item from the database.
        """

        async def endpoint(
            log: Annotated[FastAPIStructLogger, Depends()],
        ):
            log.bind(db_model=self.model.__name__)
            log.info("Purging all soft-deleted database entries")
            await self.crud.purge_all(db.session)
            log.info("All soft-deleted database entries purged successfully")

        return endpoint

    def add_routes_to_router(
        self, router: APIRouter, tags: list[str | Enum] | None = None
    ):
        router.add_api_route(
            "/all",
            self._read_items(),
            methods=["GET"],
            tags=tags,
            description=f"Read all {self.model.__name__} rows from the database.",
            operation_id=f"get_all_{self.model.__name__.lower()}",
            summary=f"Read all {self.model.__name__}",
        )
        if hasattr(self.model, "is_deleted"):
            router.add_api_route(
                "/purge",
                self._purge_all(),
                methods=["DELETE"],
                tags=tags,
                description=f"Purge all soft-deleted {self.model.__name__} items.",
                operation_id=f"purge_all_{self.model.__name__.lower()}",
                summary=f"Purge all soft-deleted {self.model.__name__}",
            )
            router.add_api_route(
                "/deleted",
                self._read_deleted(),
                methods=["GET"],
                tags=tags,
                description=f"Read all deleted {self.model.__name__} objects",
                operation_id=f"get_deleted_{self.model.__name__.lower()}",
                summary=f"Read all deleted {self.model.__name__} objects",
            )
            router.add_api_route(
                "/{id}/restore",
                self._restore_item(),
                methods=["PATCH"],
                tags=tags,
                description=f"Restore a soft-deleted {self.model.__name__} item from the database.",
                operation_id=f"restore_{self.model.__name__.lower()}",
                summary=f"Restore a single {self.model.__name__}",
            )
            router.add_api_route(
                "/{id}/purge",
                self._purge_item(),
                methods=["DELETE"],
                tags=tags,
                description=f"Purge a soft-deleted {self.model.__name__} item from the database.",
                operation_id=f"purge_{self.model.__name__.lower()}",
                summary=f"Purge a single {self.model.__name__}",
            )
        router.add_api_route(
            "/{id}",
            self._read_item(),
            methods=["GET"],
            tags=tags,
            description=f"Read a single {self.model.__name__} row from the database.",
            operation_id=f"get_{self.model.__name__.lower()}",
            summary=f"Read a single {self.model.__name__}",
        )
        router.add_api_route(
            "/{id}",
            self._update_item(),
            methods=["PATCH"],
            tags=tags,
            description=f"Update a single {self.model.__name__} in the database.",
            operation_id=f"update_{self.model.__name__.lower()}",
            summary=f"Update a {self.model.__name__}",
        )
        router.add_api_route(
            "/{id}",
            self._delete_item(),
            methods=["DELETE"],
            tags=tags,
            description=(
                f"Delete a single {self.model.__name__} from the database. Will soft delete"
                " if model has deleted_at field."
            ),
            operation_id=f"delete_{self.model.__name__.lower()}",
            summary=f"Delete a single {self.model.__name__}",
        )
        router.add_api_route(
            "",
            self._read_paginated(),
            methods=["GET"],
            tags=tags,
            description=f"Read paginated {self.model.__name__} rows from the database.",
            operation_id=f"get_paginated_{self.model.__name__.lower()}",
            summary=f"Read paginated {self.model.__name__}",
        )
        router.add_api_route(
            "",
            self._create_item(),
            methods=["POST"],
            tags=tags,
            description=f"Create a new {self.model.__name__} row in the database.",
            operation_id=f"create_{self.model.__name__.lower()}",
            summary=f"Create a new {self.model.__name__}",
        )
