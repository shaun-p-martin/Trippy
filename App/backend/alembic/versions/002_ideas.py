"""ideas comments reactions

Revision ID: 002
Revises: 001
Create Date: 2026-07-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    idea_types_type = (
        postgresql.JSONB() if bind.dialect.name == "postgresql" else sa.JSON()
    )

    op.create_table(
        "ideas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location_text", sa.String(length=500), nullable=True),
        sa.Column("apple_maps_url", sa.String(length=1000), nullable=True),
        sa.Column("google_maps_url", sa.String(length=1000), nullable=True),
        sa.Column("idea_types", idea_types_type, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("official_website", sa.String(length=1000), nullable=True),
        sa.Column("contact_phone", sa.String(length=40), nullable=True),
        sa.Column("contact_email", sa.String(length=320), nullable=True),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["travelers.id"]),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ideas_created_by_id"), "ideas", ["created_by_id"], unique=False)
    op.create_index(op.f("ix_ideas_trip_id"), "ideas", ["trip_id"], unique=False)

    op.create_table(
        "idea_comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["travelers.id"]),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["idea_comments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_idea_comments_created_by_id"), "idea_comments", ["created_by_id"], unique=False)
    op.create_index(op.f("ix_idea_comments_idea_id"), "idea_comments", ["idea_id"], unique=False)
    op.create_index(op.f("ix_idea_comments_parent_id"), "idea_comments", ["parent_id"], unique=False)

    op.create_table(
        "idea_reactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idea_id", sa.Uuid(), nullable=False),
        sa.Column("traveler_id", sa.Uuid(), nullable=False),
        sa.Column("reaction_type", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["traveler_id"], ["travelers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idea_id", "traveler_id", "reaction_type", name="uq_idea_reaction"),
    )
    op.create_index(op.f("ix_idea_reactions_idea_id"), "idea_reactions", ["idea_id"], unique=False)
    op.create_index(op.f("ix_idea_reactions_traveler_id"), "idea_reactions", ["traveler_id"], unique=False)


def downgrade() -> None:
    op.drop_table("idea_reactions")
    op.drop_table("idea_comments")
    op.drop_table("ideas")
