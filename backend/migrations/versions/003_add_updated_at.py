"""Add updated_at to specs

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:02.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at column to specs table
    op.add_column("specs", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Set default value for existing records
    op.execute("UPDATE specs SET updated_at = created_at WHERE updated_at IS NULL")


def downgrade() -> None:
    # Remove updated_at column
    op.drop_column("specs", "updated_at")
