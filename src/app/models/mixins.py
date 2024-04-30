"""
Database model mixins common to all models.
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """
    UUID Mixin
    """

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )


class TimestampMixin:
    """
    Timestamp Mixin for created_at and updated_at
    """

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(),
        server_default=text("current_timestamp(0)"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        onupdate=datetime.now(),
        server_default=text("current_timestamp(0)"),
    )


class SoftDeleteMixin:
    """
    Soft Delete Mixin
    """

    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
