from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.population import PopulationCreate, PopulationUpdate, PopulationResponse
from backend.app.services.population_service import (
    create_population,
    get_population_records,
    get_population_by_id,
    update_population,
    delete_population,
)

router = APIRouter(prefix="/population", tags=["Population"])


@router.post("", response_model=PopulationResponse, status_code=status.HTTP_201_CREATED)
def create_new_population(pop_in: PopulationCreate, db: Session = Depends(get_db)):
    """Create a new population demographics record."""
    return create_population(db=db, pop_in=pop_in)


@router.get("", response_model=List[PopulationResponse])
def list_population(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Retrieve list of population records."""
    return get_population_records(db=db, skip=skip, limit=limit)


@router.get("/{pop_id}", response_model=PopulationResponse)
def get_population(pop_id: int, db: Session = Depends(get_db)):
    """Get a specific population record by ID."""
    return get_population_by_id(db=db, pop_id=pop_id)


@router.put("/{pop_id}", response_model=PopulationResponse)
def update_existing_population(
    pop_id: int, pop_in: PopulationUpdate, db: Session = Depends(get_db)
):
    """Update a population record."""
    return update_population(db=db, pop_id=pop_id, pop_in=pop_in)


@router.delete("/{pop_id}", status_code=status.HTTP_200_OK)
def remove_population(pop_id: int, db: Session = Depends(get_db)):
    """Delete a population record."""
    return delete_population(db=db, pop_id=pop_id)
