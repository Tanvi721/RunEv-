"""add user preferences

Revision ID: 0004_add_user_preferences
Revises: 0003_add_request_otp
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_add_user_preferences"
down_revision = "0003_add_request_otp"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme_mode", sa.String(length=32), nullable=True),
        sa.Column("brand_color", sa.String(length=32), nullable=True),
        sa.Column("accent_color", sa.String(length=32), nullable=True),
        sa.Column("gradient_start", sa.String(length=32), nullable=True),
        sa.Column("gradient_end", sa.String(length=32), nullable=True),
        sa.Column("card_appearance", sa.String(length=32), nullable=True),
        sa.Column("border_radius_style", sa.String(length=32), nullable=True),
        sa.Column("dashboard_density", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_preferences_id"), "user_preferences", ["id"], unique=False)
    op.create_index(op.f("ix_user_preferences_user_id"), "user_preferences", ["user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_user_preferences_user_id"), table_name="user_preferences")
    op.drop_index(op.f("ix_user_preferences_id"), table_name="user_preferences")
    op.drop_table("user_preferences")
