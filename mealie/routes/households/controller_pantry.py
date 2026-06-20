from datetime import UTC, datetime
from functools import cached_property

import sqlalchemy as sa
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import UUID4

from mealie.db.models.household.household_to_recipe import HouseholdToRecipe
from mealie.db.models.recipe.ingredient import IngredientFoodModel, RecipeIngredientModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema.household.pantry import (
    CookingCheckRequest,
    PantryItemCreate,
    PantryItemRead,
    PantryItemUpdate,
)

router = APIRouter(prefix="/households/pantry", tags=["Households: Pantry"], route_class=MealieCrudRoute)


@controller(router)
class PantryController(BaseCrudController):
    @cached_property
    def pantry(self):
        return self.repos.pantry

    # ================================================================
    # CRUD

    @router.get("", response_model=list[PantryItemRead])
    def get_all(
        self,
        location: str | None = Query(None),
        category: str | None = Query(None),
    ):
        """List all pantry items for the current household, optionally filtered by location or category."""
        items = self.pantry.get_all()
        if location:
            items = [i for i in items if i.location == location]
        if category:
            items = [i for i in items if i.category == category]
        return items

    @router.post("", response_model=PantryItemRead, status_code=status.HTTP_201_CREATED)
    def create_one(self, data: PantryItemCreate):
        """Create a new pantry item."""
        data_dict = data.model_dump()
        data_dict["household_id"] = self.household_id
        data_dict["group_id"] = self.group_id
        data_dict["last_updated"] = datetime.now(UTC)
        return self.pantry.create(data_dict)

    @router.get("/recipe/{slug}/ingredients", response_model=list[dict])
    def get_recipe_pantry_cross_ref(self, slug: str):
        """Return recipe ingredients cross-referenced with pantry items for the cooking-check dialog."""
        group_recipes = get_repositories(self.session, group_id=self.group_id, household_id=None).recipes
        recipe = group_recipes.get_one(slug, "slug")
        if not recipe:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

        result = []
        for ingredient in recipe.recipe_ingredient or []:
            food = ingredient.food
            pantry_items = []
            if food:
                pantry_items = self.pantry.get_by_food_id(food.id)

            result.append(
                {
                    "reference_id": str(ingredient.reference_id) if ingredient.reference_id else None,
                    "food_id": str(food.id) if food else None,
                    "food_name": food.name if food else ingredient.note,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit.name if ingredient.unit else None,
                    "pantry_items": [
                        {
                            "id": str(p.id),
                            "name": p.name,
                            "location": p.location,
                            "category": p.category,
                            "quantity": p.quantity,
                            "unit": p.unit,
                            "is_low": p.is_low,
                            "is_out": p.is_out,
                            "expiration_date": p.expiration_date.isoformat() if p.expiration_date else None,
                        }
                        for p in pantry_items
                    ],
                }
            )
        return result

    @router.post("/cooking-check", status_code=status.HTTP_200_OK)
    def cooking_check(self, data: CookingCheckRequest):
        """Post-cooking ingredient check: update pantry items, auto-creating if absent."""
        for depletion in data.depletions:
            existing = self.pantry.get_by_food_id(depletion.food_id)
            if not existing:
                # Auto-create a new pantry item for this food
                food = self.session.get(IngredientFoodModel, str(depletion.food_id))
                if food:
                    self.pantry.create({
                        "name": food.name,
                        "food_id": depletion.food_id,
                        "quantity": depletion.quantity,
                        "unit": depletion.unit,
                        "location": depletion.location,
                        "category": depletion.category,
                        "expiration_date": depletion.expiration_date,
                        "is_low": depletion.status == "low",
                        "is_out": depletion.status == "out",
                        "household_id": self.household_id,
                        "group_id": self.group_id,
                        "last_updated": datetime.now(UTC),
                    })
            else:
                self.pantry.mark_depleted(
                    depletion.food_id, depletion.status, depletion.quantity, depletion.expiration_date, depletion.unit
                )
        self.session.commit()
        return {"message": "Pantry updated successfully"}

    @router.put("/{item_id}", response_model=PantryItemRead)
    def update_one(self, item_id: UUID4, data: PantryItemUpdate):
        """Update a pantry item."""
        existing = self.pantry.get_one(str(item_id))
        if not existing or str(existing.household_id) != str(self.household_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pantry item not found")

        update_dict = data.model_dump(exclude_unset=True)
        update_dict["last_updated"] = datetime.now(UTC)
        return self.pantry.patch(str(item_id), update_dict)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_one(self, item_id: UUID4):
        """Delete a pantry item."""
        existing = self.pantry.get_one(str(item_id))
        if not existing or str(existing.household_id) != str(self.household_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pantry item not found")

        self.pantry.delete(str(item_id))

    # ================================================================
    # Ingredient Suggestions

    @router.get("/suggestions/ingredients", response_model=list[dict])
    def get_ingredient_suggestions(self, limit: int = Query(default=10, ge=1, le=50)):
        """Return the most frequently used ingredient foods across this household's cooked recipes."""
        # Join HouseholdToRecipe → RecipeModel → RecipeIngredientModel → IngredientFoodModel
        stmt = (
            sa.select(
                IngredientFoodModel.id,
                IngredientFoodModel.name,
                sa.func.count(RecipeIngredientModel.id).label("frequency"),
            )
            .join(RecipeIngredientModel, RecipeIngredientModel.food_id == IngredientFoodModel.id)
            .join(RecipeModel, RecipeModel.id == RecipeIngredientModel.recipe_id)
            .join(HouseholdToRecipe, HouseholdToRecipe.recipe_id == RecipeModel.id)
            .filter(HouseholdToRecipe.household_id == str(self.household_id))
            .filter(IngredientFoodModel.id.is_not(None))
            .group_by(IngredientFoodModel.id, IngredientFoodModel.name)
            .order_by(sa.desc("frequency"))
            .limit(limit)
        )

        rows = self.session.execute(stmt).all()
        return [{"id": str(row.id), "name": row.name, "frequency": row.frequency} for row in rows]
