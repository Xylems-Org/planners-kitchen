"""Add recipe fork lineage (parent_recipe_id, fork_note)

Revision ID: a1b2c3d4e5f6
Revises: 1d9a002d7234
Create Date: 2026-02-24 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision: str | None = "2187537c52b8"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("parent_recipe_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.add_column(sa.Column("fork_note", sa.String(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_recipes_parent_recipe_id"), ["parent_recipe_id"], unique=False
        )
        batch_op.create_foreign_key("fk_recipe_parent", "recipes", ["parent_recipe_id"], ["id"])


def downgrade():
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.drop_constraint("fk_recipe_parent", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_recipes_parent_recipe_id"))
        batch_op.drop_column("fork_note")
        batch_op.drop_column("parent_recipe_id")
