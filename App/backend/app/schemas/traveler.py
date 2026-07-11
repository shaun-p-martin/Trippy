from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TravelerPublic(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    display_name: str | None
    mobile: str | None
    venmo_username: str | None
    cashapp_username: str | None
    zelle_email: str | None
    zelle_phone: str | None
    lightning_address: str | None
    crypto_wallet_address: str | None
    crypto_chain: str | None
    preferred_currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TravelerUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)
    mobile: str | None = Field(default=None, max_length=40)
    venmo_username: str | None = Field(default=None, max_length=100)
    cashapp_username: str | None = Field(default=None, max_length=100)
    zelle_email: str | None = None
    zelle_phone: str | None = Field(default=None, max_length=40)
    lightning_address: str | None = Field(default=None, max_length=255)
    crypto_wallet_address: str | None = Field(default=None, max_length=255)
    crypto_chain: str | None = Field(default=None, max_length=50)
    preferred_currency: str | None = Field(default=None, min_length=3, max_length=3)
