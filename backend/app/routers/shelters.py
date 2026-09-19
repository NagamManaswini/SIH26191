from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import Shelter
from backend.app.schemas.shelter import (
    ShelterCreate,
    ShelterUpdate,
    ShelterResponse,
    ShelterCapacityMetricsResponse,
    ShelterEvaluateRequest,
    ShelterEvaluateResponse,
)
from backend.app.services.shelter_service import (
    create_shelter,
    get_shelters,
    get_shelter_by_id,
    update_shelter,
    delete_shelter,
)
from backend.app.services.capacity_engine import (
    evaluate_shelter_capacity,
    evaluate_evacuee_assignment,
)

router = APIRouter(prefix="/shelters", tags=["Shelters"])


@router.post("", response_model=ShelterResponse, status_code=status.HTTP_201_CREATED)
def create_new_shelter(shelter_in: ShelterCreate, db: Session = Depends(get_db)):
    """Create a new shelter record with spatial point coordinates."""
    return create_shelter(db=db, shelter_in=shelter_in)


@router.get("", response_model=List[ShelterResponse])
def list_shelters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """Retrieve list of shelters with optional status filtering."""
    return get_shelters(db=db, skip=skip, limit=limit, status_filter=status_filter)


@router.get("/capacity", response_model=List[ShelterCapacityMetricsResponse])
def get_all_shelter_capacities(
    min_available_capacity: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    """Get carrying capacity assessment, suitability score, and resource metrics for all shelters."""
    shelters = db.query(Shelter).all()
    evaluated = [evaluate_shelter_capacity(s, db) for s in shelters]

    if min_available_capacity is not None:
        evaluated = [e for e in evaluated if e.available_capacity >= min_available_capacity]

    evaluated.sort(key=lambda x: x.overall_suitability, reverse=True)
    return evaluated


@router.get("/{shelter_id}/capacity", response_model=ShelterCapacityMetricsResponse)
def get_shelter_capacity_by_id(shelter_id: int, db: Session = Depends(get_db)):
    """Get detailed carrying capacity metrics for a specific shelter by ID."""
    shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
    if not shelter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shelter with id {shelter_id} not found",
        )
    return evaluate_shelter_capacity(shelter, db)


@router.post("/evaluate", response_model=ShelterEvaluateResponse, status_code=status.HTTP_200_OK)
def evaluate_shelter_relocation(req: ShelterEvaluateRequest, db: Session = Depends(get_db)):
    """Evaluate evacuee population assignment against available shelters without exceeding capacity limits."""
    shelters = db.query(Shelter).all()
    return evaluate_evacuee_assignment(req=req, shelters=shelters, db=db)


@router.get("/{shelter_id}", response_model=ShelterResponse)
def get_shelter(shelter_id: int, db: Session = Depends(get_db)):
    """Get a specific shelter by ID."""
    return get_shelter_by_id(db=db, shelter_id=shelter_id)


@router.put("/{shelter_id}", response_model=ShelterResponse)
def update_existing_shelter(
    shelter_id: int, shelter_in: ShelterUpdate, db: Session = Depends(get_db)
):
    """Update a shelter record. Prevents setting occupancy greater than capacity."""
    return update_shelter(db=db, shelter_id=shelter_id, shelter_in=shelter_in)


@router.delete("/{shelter_id}", status_code=status.HTTP_200_OK)
def remove_shelter(shelter_id: int, db: Session = Depends(get_db)):
    """Delete a shelter record."""
    return delete_shelter(db=db, shelter_id=shelter_id)
