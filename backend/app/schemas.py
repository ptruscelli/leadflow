""" Pydantic schemas for API endpoints """

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum


class LeadBase(BaseModel):
    # base model for lead
    name: str = Field(..., min_length=3, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(description="Phone number")
    message: str = Field(description="Message")


class LeadCreate(LeadBase):
    # create new lead from frontend form
    pass


class LeadStatus(str, Enum):
    # allowed values for updating lead status
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    closed = "closed"


class LeadRead(LeadBase):
    # read lead from database
    # combines base model with complete lead data
    id: int
    status: LeadStatus
    note: str | None
    created_at: datetime
    updated_at: datetime


class LeadUpdate(BaseModel):
    # update status and/or note
    # | None = none allows updating only one field
    status: LeadStatus | None = None
    note:str | None = None
