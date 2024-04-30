from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .ability import Ability


class Hero(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "heroes"

    name: Mapped[str] = mapped_column(nullable=False)
    ability_id: Mapped[int] = mapped_column(ForeignKey("abilities.id"))
    ability: Mapped["Ability"] = relationship(back_populates="heroes")
