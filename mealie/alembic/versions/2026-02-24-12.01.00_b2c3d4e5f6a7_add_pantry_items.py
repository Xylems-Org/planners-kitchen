"""Add pantry_items table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-24 12:01:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.create_table(
        "pantry_items",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.Column("household_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("food_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("is_low", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_out", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["food_id"], ["ingredient_foods.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["household_id"], ["households.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("pantry_items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_pantry_items_household_id"), ["household_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_pantry_items_group_id"), ["group_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_pantry_items_food_id"), ["food_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_pantry_items_location"), ["location"], unique=False)


def downgrade():
    with op.batch_alter_table("pantry_items", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_pantry_items_location"))
        batch_op.drop_index(batch_op.f("ix_pantry_items_food_id"))
        batch_op.drop_index(batch_op.f("ix_pantry_items_group_id"))
        batch_op.drop_index(batch_op.f("ix_pantry_items_household_id"))
    op.drop_table("pantry_items")
