"""
Initial database schema migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables"""
    # Users table
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(50), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(100), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), onupdate=sa.func.now()),
    )

    # Specs table
    op.create_table(
        "specs",
        sa.Column("spec_id", sa.String(50), primary_key=True),
        sa.Column("user_id", sa.String(50), sa.ForeignKey("users.user_id")),
        sa.Column("project_id", sa.String(100), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("spec_json", sa.JSON(), nullable=False),
        sa.Column("spec_version", sa.Integer(), default=1),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), onupdate=sa.func.now()),
    )
    op.create_index("ix_specs_user_id", "specs", ["user_id"])
    op.create_index("ix_specs_project_id", "specs", ["project_id"])

    # Iterations table
    op.create_table(
        "iterations",
        sa.Column("iter_id", sa.String(50), primary_key=True),
        sa.Column("spec_id", sa.String(50), sa.ForeignKey("specs.spec_id")),
        sa.Column("user_id", sa.String(50), nullable=True),
        sa.Column("before_spec", sa.JSON(), nullable=False),
        sa.Column("after_spec", sa.JSON(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_iterations_spec_id", "iterations", ["spec_id"])

    # Evaluations table
    op.create_table(
        "evaluations",
        sa.Column("eval_id", sa.String(50), primary_key=True),
        sa.Column("spec_id", sa.String(50), sa.ForeignKey("specs.spec_id")),
        sa.Column("user_id", sa.String(50), sa.ForeignKey("users.user_id")),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_evaluations_spec_id", "evaluations", ["spec_id"])
    op.create_index("ix_evaluations_user_id", "evaluations", ["user_id"])

    # RLHF Feedback table
    op.create_table(
        "rlhf_feedback",
        sa.Column("feedback_id", sa.String(50), primary_key=True),
        sa.Column("user_id", sa.String(50), sa.ForeignKey("users.user_id")),
        sa.Column("spec_a_id", sa.String(50), sa.ForeignKey("specs.spec_id")),
        sa.Column("spec_b_id", sa.String(50), sa.ForeignKey("specs.spec_id")),
        sa.Column("preference", sa.String(1), nullable=False),  # 'A' or 'B'
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column("rating_a", sa.Float(), nullable=True),
        sa.Column("rating_b", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_rlhf_feedback_user_id", "rlhf_feedback", ["user_id"])


def downgrade() -> None:
    """Drop tables"""
    op.drop_table("rlhf_feedback")
    op.drop_table("evaluations")
    op.drop_table("iterations")
    op.drop_table("specs")
    op.drop_table("users")
