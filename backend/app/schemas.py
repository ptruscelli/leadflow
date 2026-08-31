""" Pydantic schemas for API endpoints """

from pydantic import BaseModel, Field, EmailStr, field_serializer
from datetime import datetime, timezone
from enum import Enum


class LeadSource(str, Enum):
    # allowed values for lead source
    google = "google"
    referral = "referral"
    social_media = "social_media"
    other = "other"

class LeadStatus(str, Enum):
    # allowed values for updating lead status
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    closed = "closed"


class LeadBase(BaseModel):
    # base model for lead
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str | None = Field(None, description="Phone number")
    company: str = Field(..., min_length=1, max_length=100, description="Company name")
    message: str = Field(..., min_length=1, max_length=2000, description="Message")
    source: LeadSource = Field(..., description="How enquirer heard about agency")



class LeadCreate(LeadBase):
    # create new lead from frontend form
    model_config = {"extra": "forbid"}
    pass


class LeadRead(LeadBase):
    # read lead from database
    # combines base model with complete lead data
    model_config = {"from_attributes": True}

    id: int
    status: LeadStatus
    note: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


    @field_serializer("created_at", "updated_at", "deleted_at")
    def serialize_dt(self, value: datetime | None):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()


class LeadUpdate(BaseModel):
    # update status and/or note
    # | None = none allows updating only one field
    model_config = {"extra": "forbid"}
    status: LeadStatus | None = None
    note:str | None = None

class LeadsResponsePaginated(BaseModel):
    leads: list[LeadRead]
    page: int
    page_size: int
    total_pages: int
    total_items: int
# AUTH

class MagicLinkRequest(BaseModel):
    model_config = {"extra": "forbid"}
    email: EmailStr = Field(..., description="Email address")


class LoginRequest(BaseModel):
    model_config = {"extra": "forbid"}
    raw_token: str = Field(..., min_length=1, description="Magic link token")