"""add service request otp

Revision ID: 0003_add_request_otp
Revises: 0002_add_ratings
Create Date: 2026-05-17
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_request_otp"
down_revision = "0002_add_ratings"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("service_requests", sa.Column("otp_code", sa.String(length=10), nullable=True))
    op.add_column("service_requests", sa.Column("otp_verified_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("service_requests", "otp_verified_at")
    op.drop_column("service_requests", "otp_code")
