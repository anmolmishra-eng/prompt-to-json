"""Seed data

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:01.000000

"""
import datetime
import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Define table structures for data insertion
    specs_table = table(
        "specs",
        column("spec_id", sa.String),
        column("user_id", sa.String),
        column("project_id", sa.String),
        column("prompt", sa.Text),
        column("spec_json", sa.JSON),
        column("spec_version", sa.Integer),
        column("created_at", sa.DateTime),
    )

    # Sample project data
    sample_specs = [
        {
            "spec_id": "spec_001",
            "user_id": "user_demo",
            "project_id": "proj_ecommerce",
            "prompt": "Create an e-commerce product catalog system",
            "spec_json": {
                "components": ["ProductList", "ProductDetail", "ShoppingCart"],
                "features": ["search", "filter", "pagination"],
                "tech_stack": ["React", "Node.js", "PostgreSQL"],
            },
            "spec_version": 1,
            "created_at": datetime.datetime.utcnow(),
        },
        {
            "spec_id": "spec_002",
            "user_id": "user_demo",
            "project_id": "proj_dashboard",
            "prompt": "Build an analytics dashboard for business metrics",
            "spec_json": {
                "components": ["MetricsWidget", "ChartComponent", "FilterPanel"],
                "features": ["real-time updates", "export", "drill-down"],
                "tech_stack": ["Vue.js", "Express", "MongoDB"],
            },
            "spec_version": 1,
            "created_at": datetime.datetime.utcnow(),
        },
    ]

    # Insert sample data
    op.bulk_insert(specs_table, sample_specs)


def downgrade() -> None:
    # Remove seed data
    op.execute("DELETE FROM specs WHERE spec_id IN ('spec_001', 'spec_002')")
