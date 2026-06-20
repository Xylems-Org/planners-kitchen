from datetime import date, datetime
from typing import Any

from pydantic import UUID4, ConfigDict, Field, field_validator

from mealie.schema._mealie import MealieModel


class PantryItemCreate(MealieModel):
    name: str
    food_id: UUID4 | None = None
    location: str | None = None
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    notes: str | None = None
    is_low: bool = False
    is_out: bool = False
    expiration_date: date | None = None


class PantryItemRead(MealieModel):
    id: UUID4
    household_id: UUID4
    group_id: UUID4

    name: str
    food_id: UUID4 | None = None
    location: str | None = None
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    notes: str | None = None
    is_low: bool = False
    is_out: bool = False
    last_updated: datetime | None = None
    expiration_date: date | None = None

    model_config = ConfigDict(from_attributes=True)


class PantryItemUpdate(MealieModel):
    name: str | None = None
    food_id: UUID4 | None = None
    location: str | None = None
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    notes: str | None = None
    is_low: bool | None = None
    is_out: bool | None = None
    expiration_date: date | None = None


class PantryItemSummary(MealieModel):
    id: UUID4
    name: str
    location: str | None = None
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    is_low: bool = False
    is_out: bool = False

    model_config = ConfigDict(from_attributes=True)


class PantryItemBulkUpdate(MealieModel):
    """Used for bulk marking items low/out (e.g. post-cooking)"""

    updates: list[PantryItemUpdate] = Field(default_factory=list)


class CookingCheckDepletion(MealieModel):
    food_id: UUID4
    status: str  # "out" | "low" | "ok"
    quantity: float | None = None
    unit: str | None = None
    location: str | None = None
    category: str | None = None
    expiration_date: date | None = None


class CookingCheckRequest(MealieModel):
    recipe_slug: str
    depletions: list[CookingCheckDepletion] = Field(default_factory=list)
