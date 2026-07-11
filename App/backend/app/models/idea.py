import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.enums import ReactionType

# JSONB on Postgres; JSON elsewhere (e.g. SQLite smoke tests)
IdeaTypesColumn = JSON().with_variant(JSONB(), "postgresql")


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    apple_maps_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    google_maps_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    idea_types: Mapped[list] = mapped_column(IdeaTypesColumn, nullable=False, default=list)
    official_website: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("travelers.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trip = relationship("Trip", back_populates="ideas")
    created_by = relationship("Traveler")
    comments = relationship("IdeaComment", back_populates="idea", cascade="all, delete-orphan")
    reactions = relationship("IdeaReaction", back_populates="idea", cascade="all, delete-orphan")


class IdeaComment(Base):
    __tablename__ = "idea_comments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    idea_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("idea_comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("travelers.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    idea = relationship("Idea", back_populates="comments")
    created_by = relationship("Traveler")
    parent = relationship("IdeaComment", remote_side="IdeaComment.id", back_populates="replies")
    replies = relationship("IdeaComment", back_populates="parent", cascade="all, delete-orphan")


class IdeaReaction(Base):
    __tablename__ = "idea_reactions"
    __table_args__ = (
        UniqueConstraint("idea_id", "traveler_id", "reaction_type", name="uq_idea_reaction"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    idea_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    traveler_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("travelers.id"), nullable=False, index=True
    )
    reaction_type: Mapped[ReactionType] = mapped_column(
        Enum(
            ReactionType,
            name="reaction_type",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=ReactionType.like,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    idea = relationship("Idea", back_populates="reactions")
    traveler = relationship("Traveler")
