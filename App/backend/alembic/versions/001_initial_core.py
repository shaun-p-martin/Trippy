"""initial core domain

Revision ID: 001
Revises:
Create Date: 2026-07-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "travelers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=150), nullable=True),
        sa.Column("mobile", sa.String(length=40), nullable=True),
        sa.Column("venmo_username", sa.String(length=100), nullable=True),
        sa.Column("cashapp_username", sa.String(length=100), nullable=True),
        sa.Column("zelle_email", sa.String(length=320), nullable=True),
        sa.Column("zelle_phone", sa.String(length=40), nullable=True),
        sa.Column("lightning_address", sa.String(length=255), nullable=True),
        sa.Column("crypto_wallet_address", sa.String(length=255), nullable=True),
        sa.Column("crypto_chain", sa.String(length=50), nullable=True),
        sa.Column("preferred_currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_travelers_email"), "travelers", ["email"], unique=True)

    op.create_table(
        "trips",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["travelers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tripmates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("traveler_id", sa.Uuid(), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("invite_email", sa.String(length=320), nullable=True),
        sa.Column("invite_token", sa.String(length=64), nullable=True),
        sa.Column("invite_status", sa.String(length=32), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["traveler_id"], ["travelers.id"]),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_id", "traveler_id", name="uq_tripmate_trip_traveler"),
    )
    op.create_index(op.f("ix_tripmates_invite_token"), "tripmates", ["invite_token"], unique=True)
    op.create_index(op.f("ix_tripmates_traveler_id"), "tripmates", ["traveler_id"], unique=False)
    op.create_index(op.f("ix_tripmates_trip_id"), "tripmates", ["trip_id"], unique=False)

    op.create_table(
        "trip_stops",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("location_name", sa.String(length=200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trip_stops_trip_id"), "trip_stops", ["trip_id"], unique=False)

    op.create_table(
        "trip_stop_mate_dates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_stop_id", sa.Uuid(), nullable=False),
        sa.Column("tripmate_id", sa.Uuid(), nullable=False),
        sa.Column("arrival_date", sa.Date(), nullable=True),
        sa.Column("departure_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["trip_stop_id"], ["trip_stops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tripmate_id"], ["tripmates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_stop_id", "tripmate_id", name="uq_stop_mate"),
    )
    op.create_index(
        op.f("ix_trip_stop_mate_dates_trip_stop_id"), "trip_stop_mate_dates", ["trip_stop_id"], unique=False
    )
    op.create_index(
        op.f("ix_trip_stop_mate_dates_tripmate_id"), "trip_stop_mate_dates", ["tripmate_id"], unique=False
    )


def downgrade() -> None:
    op.drop_table("trip_stop_mate_dates")
    op.drop_table("trip_stops")
    op.drop_table("tripmates")
    op.drop_table("trips")
    op.drop_table("travelers")
