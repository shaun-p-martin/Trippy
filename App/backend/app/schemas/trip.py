from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import InviteStatus, TripmateRole


class TripCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class TripUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_archived: bool | None = None


class TripSummary(BaseModel):
    id: UUID
    name: str
    description: str | None
    start_date: date | None
    end_date: date | None
    is_archived: bool
    my_role: TripmateRole
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TripDetail(TripSummary):
    created_by_id: UUID


class TripStopCreate(BaseModel):
    location_name: str = Field(min_length=1, max_length=200)
    sort_order: int = 0


class TripStopUpdate(BaseModel):
    location_name: str | None = Field(default=None, min_length=1, max_length=200)
    sort_order: int | None = None


class TripStopRead(BaseModel):
    id: UUID
    trip_id: UUID
    location_name: str
    sort_order: int
    earliest_arrival: date | None = None
    latest_departure: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TripmateRead(BaseModel):
    id: UUID
    trip_id: UUID
    traveler_id: UUID | None
    role: TripmateRole
    invite_email: str | None
    invite_status: InviteStatus
    joined_at: datetime | None
    traveler_display: str | None = None

    model_config = {"from_attributes": True}


class InviteCreate(BaseModel):
    email: EmailStr
    role: TripmateRole = TripmateRole.contributor


class InviteCreateResponse(BaseModel):
    tripmate: TripmateRead
    invite_token: str


class TripmateRoleUpdate(BaseModel):
    role: TripmateRole
