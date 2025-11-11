"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create specs table
    op.create_table('specs',
    sa.Column('spec_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('project_id', sa.String(), nullable=True),
    sa.Column('prompt', sa.Text(), nullable=True),
    sa.Column('spec_json', sa.JSON(), nullable=True),
    sa.Column('spec_version', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('spec_id')
    )
    op.create_index(op.f('ix_specs_project_id'), 'specs', ['project_id'], unique=False)
    op.create_index(op.f('ix_specs_user_id'), 'specs', ['user_id'], unique=False)

    # Create evaluations table
    op.create_table('evaluations',
    sa.Column('eval_id', sa.String(), nullable=False),
    sa.Column('spec_id', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('ts', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['spec_id'], ['specs.spec_id'], ),
    sa.PrimaryKeyConstraint('eval_id')
    )
    op.create_index(op.f('ix_evaluations_user_id'), 'evaluations', ['user_id'], unique=False)

    # Create iterations table
    op.create_table('iterations',
    sa.Column('iter_id', sa.String(), nullable=False),
    sa.Column('spec_id', sa.String(), nullable=True),
    sa.Column('before_spec', sa.JSON(), nullable=True),
    sa.Column('after_spec', sa.JSON(), nullable=True),
    sa.Column('feedback', sa.Text(), nullable=True),
    sa.Column('ts', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['spec_id'], ['specs.spec_id'], ),
    sa.PrimaryKeyConstraint('iter_id')
    )

    # Create audit_logs table
    op.create_table('audit_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('event', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('ts', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('iterations')
    op.drop_index(op.f('ix_evaluations_user_id'), table_name='evaluations')
    op.drop_table('evaluations')
    op.drop_index(op.f('ix_specs_user_id'), table_name='specs')
    op.drop_index(op.f('ix_specs_project_id'), table_name='specs')
    op.drop_table('specs')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')