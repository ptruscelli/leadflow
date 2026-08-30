

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Annotated
from math import ceil

from app.schemas import LeadCreate, LeadUpdate, LeadRead, LeadsResponsePaginated
from app.models import Lead
from app.deps import require_session, get_db


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
@router.get("", response_model=LeadsResponsePaginated)
def get_leads(
    db: Session = Depends(get_db),
    _email: str = Depends(require_session),
    deleted: bool = False,
    page: Annotated[int, Query(ge=1)] = 1, # page number
    page_size: Annotated[int, Query(ge=1, le=10)] = 10, # max 10 leads per page
):
    # filter active leads or archive from deleted=true or false query param
    if deleted:
        deleted_filter = Lead.deleted_at.is_not(None)
    else:
        deleted_filter = Lead.deleted_at.is_(None)

    total_leads= db.scalar(select(func.count()).select_from(Lead).where(deleted_filter)) or 0
    total_pages = ceil(total_leads / page_size) if total_leads else 0 # round up so leftover leads are on next page

    offset = (page - 1) * page_size # pages counted from 1, but SQL OFFSET is from 0

    stmt = (
        select(Lead)
        .where(deleted_filter)
        .order_by(Lead.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    leads = db.scalars(stmt).all()

    return LeadsResponsePaginated(
        leads=leads,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_items=total_leads,
    )


# GET /leads/{id} | open lead to see full enquiry
@router.get("/{id}", response_model=LeadRead)
def get_lead(
    id: int,
    db: Session = Depends(get_db),
    _email: str = Depends(require_session)):

    lead = db.get(Lead, id)

    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead


# PATCH /leads/{id}| update lead status or add/edit note
@router.patch("/{id}", response_model=LeadRead)
def update_lead(
    id: int,
    body: LeadUpdate,
    db: Session = Depends(get_db),
    _email: str = Depends(require_session)):

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
def delete_lead(
    id: int,
    db: Session = Depends(get_db),
    _email: str = Depends(require_session)):
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
