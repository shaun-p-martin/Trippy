from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import IdeaType, ReactionType


class IdeaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    location_text: str | None = Field(default=None, max_length=500)
    apple_maps_url: str | None = Field(default=None, max_length=1000)
    google_maps_url: str | None = Field(default=None, max_length=1000)
    idea_types: list[IdeaType] = Field(default_factory=list)
    official_website: str | None = Field(default=None, max_length=1000)
    contact_phone: str | None = Field(default=None, max_length=40)
    contact_email: EmailStr | None = None


class IdeaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    location_text: str | None = Field(default=None, max_length=500)
    apple_maps_url: str | None = Field(default=None, max_length=1000)
    google_maps_url: str | None = Field(default=None, max_length=1000)
    idea_types: list[IdeaType] | None = None
    official_website: str | None = Field(default=None, max_length=1000)
    contact_phone: str | None = Field(default=None, max_length=40)
    contact_email: EmailStr | None = None


class IdeaRead(BaseModel):
    id: UUID
    trip_id: UUID
    name: str
    description: str | None
    location_text: str | None
    apple_maps_url: str | None
    google_maps_url: str | None
    idea_types: list[IdeaType]
    official_website: str | None
    contact_phone: str | None
    contact_email: str | None
    created_by_id: UUID
    created_by_display: str | None = None
    reaction_count: int = 0
    comment_count: int = 0
    reacted_by_me: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("idea_types", mode="before")
    @classmethod
    def coerce_types(cls, value):
        if value is None:
            return []
        return value


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    parent_id: UUID | None = None


class CommentRead(BaseModel):
    id: UUID
    idea_id: UUID
    parent_id: UUID | None
    content: str
    created_by_id: UUID
    created_by_display: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReactionToggleResponse(BaseModel):
    idea_id: UUID
    reaction_type: ReactionType
    reacted: bool
    reaction_count: int
