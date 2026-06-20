from datetime import UTC, date, datetime

from pydantic import UUID4
from sqlalchemy import select

from mealie.db.models.household.pantry import PantryItem
from mealie.schema.household.pantry import PantryItemCreate, PantryItemRead, PantryItemUpdate

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryPantry(HouseholdRepositoryGeneric[PantryItemRead, PantryItem]):
    def get_by_location(self, location: str) -> list[PantryItemRead]:
        stmt = (
            select(self.model)
            .filter(self.model.household_id == self.household_id)
            .filter(self.model.location == location)
        )
        return [self.schema.model_validate(r) for r in self.session.execute(stmt).scalars().all()]

    def get_by_food_id(self, food_id: UUID4) -> list[PantryItemRead]:
        stmt = (
            select(self.model)
            .filter(self.model.household_id == self.household_id)
            .filter(self.model.food_id == str(food_id))
        )
        return [self.schema.model_validate(r) for r in self.session.execute(stmt).scalars().all()]

    def mark_depleted(
        self,
        food_id: UUID4,
        status: str,
        quantity: float | None = None,
        expiration_date: date | None = None,
        unit: str | None = None,
    ) -> None:
        """Update pantry items with given food_id: set stock status, quantity, unit and/or expiration date."""
        # Load ORM objects directly (avoids double-query via session.get + Pydantic intermediary)
        stmt = (
            select(self.model)
            .filter(self.model.household_id == self.household_id)
            .filter(self.model.food_id == str(food_id))
        )
        db_items = self.session.execute(stmt).scalars().all()
        for db_item in db_items:
            if status == "out":
                db_item.is_out = True
                db_item.is_low = True
            elif status == "low":
                db_item.is_low = True
                db_item.is_out = False
            else:
                db_item.is_low = False
                db_item.is_out = False
            if quantity is not None:
                db_item.quantity = quantity
            if expiration_date is not None:
                db_item.expiration_date = expiration_date
            if unit is not None:
                db_item.unit = unit
            db_item.last_updated = datetime.now(UTC)
        self.session.commit()
