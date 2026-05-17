"""add ratings

Revision ID: 0002_add_ratings
Revises: 0001_initial_schema
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_ratings"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("service_requests.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("request_id", name="uq_ratings_request_id"),
    )
    op.create_index("ix_ratings_id", "ratings", ["id"])
    op.create_index("ix_ratings_request_id", "ratings", ["request_id"])
    op.create_index("ix_ratings_user_id", "ratings", ["user_id"])
    op.create_index("ix_ratings_provider_id", "ratings", ["provider_id"])
    op.create_index("ix_ratings_created_at", "ratings", ["created_at"])
    op.create_index("ix_ratings_provider_score", "ratings", ["provider_id", "score"])


def downgrade():
    op.drop_index("ix_ratings_provider_score", table_name="ratings")
    op.drop_index("ix_ratings_created_at", table_name="ratings")
    op.drop_index("ix_ratings_provider_id", table_name="ratings")
    op.drop_index("ix_ratings_user_id", table_name="ratings")
    op.drop_index("ix_ratings_request_id", table_name="ratings")
    op.drop_index("ix_ratings_id", table_name="ratings")
    op.drop_table("ratings")
