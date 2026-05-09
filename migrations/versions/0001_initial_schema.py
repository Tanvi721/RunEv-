"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("vehicle_number", sa.String(length=255), nullable=True),
        sa.Column("current_lat", sa.Float(), nullable=True),
        sa.Column("current_lng", sa.Float(), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=True),
        sa.Column("charging_speed", sa.String(length=255), nullable=True),
        sa.Column("connector_types", sa.String(length=255), nullable=True),
        sa.Column("price_per_kwh", sa.Float(), nullable=True),
        sa.Column("profile_photo", sa.String(length=512), nullable=True),
        sa.Column("driver_name", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=512), nullable=True),
    )
    op.create_index("ix_providers_id", "providers", ["id"])
    op.create_index("ix_providers_user_id", "providers", ["user_id"])
    op.create_index("ix_providers_vehicle_number", "providers", ["vehicle_number"])
    op.create_index("ix_providers_current_lat", "providers", ["current_lat"])
    op.create_index("ix_providers_current_lng", "providers", ["current_lng"])
    op.create_index("ix_providers_is_available", "providers", ["is_available"])
    op.create_index("ix_providers_available_location", "providers", ["is_available", "current_lat", "current_lng"])

    op.create_table(
        "stations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=512), nullable=True),
        sa.Column("location_lat", sa.Float(), nullable=False),
        sa.Column("location_lng", sa.Float(), nullable=False),
        sa.Column("price_per_hour", sa.Float(), nullable=True),
        sa.Column("total_slots", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
    )
    op.create_index("ix_stations_id", "stations", ["id"])

    op.create_table(
        "service_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("providers.id"), nullable=True),
        sa.Column("request_time", sa.DateTime(), nullable=True),
        sa.Column("pickup_lat", sa.Float(), nullable=True),
        sa.Column("pickup_lng", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("payment_method", sa.String(length=255), nullable=True),
        sa.Column("charged_units_kwh", sa.Float(), nullable=True),
        sa.Column("total_price", sa.Float(), nullable=True),
    )
    op.create_index("ix_service_requests_id", "service_requests", ["id"])
    op.create_index("ix_service_requests_user_id", "service_requests", ["user_id"])
    op.create_index("ix_service_requests_provider_id", "service_requests", ["provider_id"])
    op.create_index("ix_service_requests_request_time", "service_requests", ["request_time"])
    op.create_index("ix_service_requests_status", "service_requests", ["status"])
    op.create_index("ix_service_requests_provider_status", "service_requests", ["provider_id", "status"])
    op.create_index("ix_service_requests_user_status", "service_requests", ["user_id", "status"])

    op.create_table(
        "slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("station_id", sa.Integer(), sa.ForeignKey("stations.id"), nullable=True),
        sa.Column("slot_number", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=True),
    )
    op.create_index("ix_slots_id", "slots", ["id"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("station_id", sa.Integer(), sa.ForeignKey("stations.id"), nullable=True),
        sa.Column("slot_id", sa.Integer(), sa.ForeignKey("slots.id"), nullable=True),
        sa.Column("booking_time", sa.DateTime(), nullable=True),
        sa.Column("duration_hours", sa.Integer(), nullable=True),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_bookings_id", "bookings", ["id"])
    op.create_index("ix_bookings_user_id", "bookings", ["user_id"])
    op.create_index("ix_bookings_station_id", "bookings", ["station_id"])
    op.create_index("ix_bookings_slot_id", "bookings", ["slot_id"])
    op.create_index("ix_bookings_booking_time", "bookings", ["booking_time"])
    op.create_index("ix_bookings_status", "bookings", ["status"])
    op.create_index("ix_bookings_user_status", "bookings", ["user_id", "status"])
    op.create_index("ix_bookings_station_slot", "bookings", ["station_id", "slot_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("service_requests.id"), nullable=True),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("razorpay_order_id", sa.String(length=255), nullable=True),
        sa.Column("razorpay_payment_id", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_payments_id", "payments", ["id"])
    op.create_index("ix_payments_request_id", "payments", ["request_id"])
    op.create_index("ix_payments_booking_id", "payments", ["booking_id"])
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_status", "payments", ["status"])


def downgrade():
    op.drop_table("payments")
    op.drop_table("bookings")
    op.drop_table("slots")
    op.drop_table("service_requests")
    op.drop_table("stations")
    op.drop_table("providers")
    op.drop_table("users")
