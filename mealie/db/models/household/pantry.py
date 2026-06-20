from datetime import UTC, date, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID


class PantryItem(SqlAlchemyBase, BaseMixins):
    __tablename__ = "pantry_items"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    household_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("households.id"), nullable=False, index=True)
    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)

    # Link to a known ingredient food (optional)
    food_id: Mapped[GUID | None] = mapped_column(
        GUID, sa.ForeignKey("ingredient_foods.id"), nullable=True, index=True
    )

    # Free-form name (used when food_id is None or for display override)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    # Free-form location: "Top shelf", "Fridge door", "Freezer", etc.
    location: Mapped[str | None] = mapped_column(sa.String, nullable=True, index=True)

    # Category: "Spices", "Dairy", "Produce", etc.
    category: Mapped[str | None] = mapped_column(sa.String, nullable=True)

    quantity: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    notes: Mapped[str | None] = mapped_column(sa.String, nullable=True)

    is_low: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    is_out: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    last_updated: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    expiration_date: Mapped[date | None] = mapped_column(sa.Date, nullable=True, index=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
