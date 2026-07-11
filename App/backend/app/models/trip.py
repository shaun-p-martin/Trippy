import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InviteStatus, TripmateRole


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("travelers.id"), nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    created_by = relationship("Traveler", back_populates="created_trips")
    tripmates = relationship("Tripmate", back_populates="trip", cascade="all, delete-orphan")
    stops = relationship(
        "TripStop", back_populates="trip", cascade="all, delete-orphan", order_by="TripStop.sort_order"
    )
    ideas = relationship("Idea", back_populates="trip", cascade="all, delete-orphan")


class Tripmate(Base):
    __tablename__ = "tripmates"
    __table_args__ = (UniqueConstraint("trip_id", "traveler_id", name="uq_tripmate_trip_traveler"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    traveler_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("travelers.id"), nullable=True, index=True
    )
    role: Mapped[TripmateRole] = mapped_column(
        Enum(
            TripmateRole,
            name="tripmate_role",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=TripmateRole.contributor,
    )
    invite_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    invite_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    invite_status: Mapped[InviteStatus] = mapped_column(
        Enum(
            InviteStatus,
            name="invite_status",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
            length=32,
        ),
        nullable=False,
        default=InviteStatus.pending,
    )
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trip = relationship("Trip", back_populates="tripmates")
    traveler = relationship("Traveler", back_populates="tripmates")
    stop_dates = relationship("TripStopMateDate", back_populates="tripmate", cascade="all, delete-orphan")


class TripStop(Base):
    __tablename__ = "trip_stops"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trip = relationship("Trip", back_populates="stops")
    mate_dates = relationship("TripStopMateDate", back_populates="trip_stop", cascade="all, delete-orphan")


class TripStopMateDate(Base):
    __tablename__ = "trip_stop_mate_dates"
    __table_args__ = (UniqueConstraint("trip_stop_id", "tripmate_id", name="uq_stop_mate"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_stop_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trip_stops.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tripmate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("tripmates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    departure_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    trip_stop = relationship("TripStop", back_populates="mate_dates")
    tripmate = relationship("Tripmate", back_populates="stop_dates")
