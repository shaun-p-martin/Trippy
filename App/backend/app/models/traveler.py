import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Traveler(Base):
    __tablename__ = "travelers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    display_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(40), nullable=True)
    venmo_username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cashapp_username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    zelle_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    zelle_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    lightning_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crypto_wallet_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crypto_chain: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tripmates = relationship("Tripmate", back_populates="traveler")
    created_trips = relationship("Trip", back_populates="created_by")
