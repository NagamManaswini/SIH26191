"""FastAPI Router for Animal Safety & Animal Shelters Module."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.animal import (
    AnimalCreate,
    AnimalUpdate,
    AnimalResponse,
    AnimalShelterCreate,
    AnimalShelterResponse,
    RescuePlanResponse,
)
from backend.app.services.animal_service import (
    get_all_animals,
    get_animal_by_id,
    create_animal,
    update_animal,
    get_animal_shelters,
    create_animal_shelter,
    generate_animal_rescue_plan,
)

router = APIRouter(prefix="/animals", tags=["Animal Safety Module"])


@router.get("", response_model=List[AnimalResponse], summary="List all animals")
def list_animals(
    emergency_status: Optional[str] = None,
    animal_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve registered animals filtered by emergency status (AT_RISK, RELOCATED) or animal type."""
    return get_all_animals(db, emergency_status=emergency_status, animal_type=animal_type)


@router.post("", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED, summary="Register an animal or herd")
def register_animal(animal_in: AnimalCreate, db: Session = Depends(get_db)):
    """Register a new animal or livestock herd for disaster safety tracking."""
    return create_animal(db, animal_in)


@router.get("/shelters", response_model=List[AnimalShelterResponse], summary="List animal safe shelters")
def list_animal_shelters(db: Session = Depends(get_db)):
    """List all dedicated animal shelters and available capacity."""
    return get_animal_shelters(db)


@router.post("/shelters", response_model=AnimalShelterResponse, status_code=status.HTTP_201_CREATED, summary="Create animal shelter")
def add_animal_shelter(shelter_in: AnimalShelterCreate, db: Session = Depends(get_db)):
    """Create a new dedicated safe holding facility for animals."""
    return create_animal_shelter(db, shelter_in)


@router.post("/rescue-plan", response_model=RescuePlanResponse, summary="Generate Animal Rescue Plan")
def run_animal_rescue_plan(db: Session = Depends(get_db)):
    """Generate optimized rescue assignment mapping Red Zone animals to Animal Shelters without mixing human capacity."""
    return generate_animal_rescue_plan(db)


@router.get("/{id}", response_model=AnimalResponse, summary="Get animal details")
def get_animal(id: int, db: Session = Depends(get_db)):
    """Get animal record by ID."""
    animal = get_animal_by_id(db, id)
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal record {id} not found.")
    return animal


@router.patch("/{id}", response_model=AnimalResponse, summary="Update animal status")
def patch_animal(id: int, animal_in: AnimalUpdate, db: Session = Depends(get_db)):
    """Update emergency status, rescue status, or assigned destination shelter."""
    updated = update_animal(db, animal_id=id, animal_in=animal_in)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Animal record {id} not found.")
    return updated
