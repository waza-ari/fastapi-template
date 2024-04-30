from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .hero import Hero


class Ability(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "abilities"

    name: Mapped[str] = mapped_column(nullable=False)
    strength: Mapped[int] = mapped_column(nullable=False)
    heroes: Mapped[list["Hero"]] = relationship(back_populates="ability")
