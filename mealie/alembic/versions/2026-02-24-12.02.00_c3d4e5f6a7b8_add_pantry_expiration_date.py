"""add pantry expiration date

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-24 12:02:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    # Idempotent: skip if the original planners-kitchen build already added these.
    insp = sa.inspect(op.get_bind())
    if not any(c["name"] == "expiration_date" for c in insp.get_columns("pantry_items")):
        op.add_column("pantry_items", sa.Column("expiration_date", sa.Date(), nullable=True))
    if not any(i["name"] == "ix_pantry_items_expiration_date" for i in sa.inspect(op.get_bind()).get_indexes("pantry_items")):
        op.create_index("ix_pantry_items_expiration_date", "pantry_items", ["expiration_date"])


def downgrade():
    op.drop_index("ix_pantry_items_expiration_date", table_name="pantry_items")
    op.drop_column("pantry_items", "expiration_date")
