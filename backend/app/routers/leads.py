

from fastapi import APIRouter
from app.schemas import LeadCreate, LeadStatus, LeadUpdate


router = APIRouter(prefix="/leads", tags=["leads"])



# POST endpoint after receiving validated form from frontend
# add data from form to database
@router.post("/")
def create_lead(body: LeadCreate):
    # create new lead in database
    return {"message": "Lead created successfully"}


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