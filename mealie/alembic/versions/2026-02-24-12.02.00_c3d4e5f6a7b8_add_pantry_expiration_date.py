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
    op.add_column("pantry_items", sa.Column("expiration_date", sa.Date(), nullable=True))
    op.create_index("ix_pantry_items_expiration_date", "pantry_items", ["expiration_date"])


def downgrade():
    op.drop_index("ix_pantry_items_expiration_date", table_name="pantry_items")
    op.drop_column("pantry_items", "expiration_date")
