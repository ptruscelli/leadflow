

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.schemas import LeadCreate, LeadUpdate, LeadRead
from app.database import get_db
from app.models import Lead


router = APIRouter(prefix="/leads", tags=["leads"])



# POST endpoint after receiving validated form from frontend
# add data from form to database

@router.post("", response_model=LeadRead, status_code=201)
def create_lead(body: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        name=body.name,
        email=body.email,
        phone=body.phone or None,
        company=body.company,
        source=body.source.value,
        message=body.message,
        status="new",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


# GET /leads | get list of leads from database
@router.get("", response_model=list[LeadRead])
def get_leads(db: Session = Depends(get_db), deleted: bool = False):
    if deleted:
        stmt = select(Lead).where(Lead.deleted_at.is_not(None))
    else:
        stmt = select(Lead).where(Lead.deleted_at.is_(None))
    stmt = stmt.order_by(Lead.created_at.desc())
    leads = db.scalars(stmt).all()
    return leads


# GET /leads/{id} | open lead to see full enquiry
@router.get("/{id}", response_model=LeadRead)
def get_lead(id: int, db: Session = Depends(get_db)):
    lead = db.get(Lead, id)

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead


# PATCH /leads/{id}| update lead status or add/edit note
@router.patch("/{id}", response_model=LeadRead)
def update_lead(id: int, body: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.get(Lead, id)

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.deleted_at is not None:
        raise HTTPException(status_code=409, detail="Cannot edit a deleted lead")

    if body.status is None and body.note is None:
        raise HTTPException(status_code=422, detail="No fields to update")

    if body.status is not None:
        lead.status = body.status
    if body.note is not None:
        lead.note = body.note or None # if user clears note (""), set to None

    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead





# DELETE /leads/{id} | soft-delete with {"deleted_at": current_time}
@router.delete("/{id}", response_model=LeadRead)
def delete_lead(id: int, db: Session = Depends(get_db)):
    lead = db.get(Lead, id)

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.deleted_at is not None:
        raise HTTPException(status_code=409, detail="Lead already deleted")

    now = datetime.now(timezone.utc) # use one timestamp for both fields
    lead.deleted_at = now
    lead.updated_at = now
    db.commit()
    db.refresh(lead)
    return lead