

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.schemas import LeadCreate, LeadStatus, LeadUpdate, LeadRead
from app.database import get_db
from app.models import Lead


router = APIRouter(prefix="/leads", tags=["leads"])



# POST endpoint after receiving validated form from frontend
# add data from form to database

@router.post("", response_model=LeadRead)

def create_lead(body: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        name=body.name,
        email=body.email,
        phone=body.phone,
        message=body.message,
        status="new",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


# GET /leads | retrieve leads from database
@router.get("/")
def get_leads():
    return {"message": "Leads retrieved successfully"}


# GET /leads/{id} | open lead to see full enquiry
@router.get("/{id}")
def get_lead(id: int):
    return {"message": "Lead retrieved successfully"}


# PATCH /leads/{id}| update lead status or add/edit note
@router.patch("/{id}")
def update_lead(id: int, body: LeadUpdate):
    return {"message": "Lead updated successfully"}


# DELETE /leads/{id} | soft-delete with something like {"archived": true}
@router.delete("/{id}")
def delete_lead(id: int):
    return {"message": "Lead deleted successfully"}