"""Service layer for Population database operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.entities import Population
from backend.app.schemas.population import PopulationCreate, PopulationUpdate, PopulationResponse


def create_population(db: Session, pop_in: PopulationCreate) -> PopulationResponse:
    if pop_in.vulnerable_population > pop_in.total_population:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vulnerable population count cannot exceed total population.",
        )

    db_pop = Population(
        location_name=pop_in.location_name,
        total_population=pop_in.total_population,
        vulnerable_population=pop_in.vulnerable_population,
        density_per_sq_km=pop_in.density_per_sq_km,
        location_id=pop_in.location_id,
    )
    db.add(db_pop)
    db.commit()
    db.refresh(db_pop)
    return PopulationResponse.model_validate(db_pop)


def get_population_records(db: Session, skip: int = 0, limit: int = 100) -> List[PopulationResponse]:
    records = db.query(Population).offset(skip).limit(limit).all()
    return [PopulationResponse.model_validate(r) for r in records]


def get_population_by_id(db: Session, pop_id: int) -> PopulationResponse:
    record = db.query(Population).filter(Population.id == pop_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Population record with id {pop_id} not found",
        )
    return PopulationResponse.model_validate(record)


def update_population(db: Session, pop_id: int, pop_in: PopulationUpdate) -> PopulationResponse:
    record = db.query(Population).filter(Population.id == pop_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Population record with id {pop_id} not found",
        )

    update_data = pop_in.model_dump(exclude_unset=True)
    new_total = update_data.get("total_population", record.total_population)
    new_vuln = update_data.get("vulnerable_population", record.vulnerable_population)
    if new_vuln > new_total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vulnerable population count cannot exceed total population.",
        )

    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return PopulationResponse.model_validate(record)


def delete_population(db: Session, pop_id: int) -> dict:
    record = db.query(Population).filter(Population.id == pop_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Population record with id {pop_id} not found",
        )
    db.delete(record)
    db.commit()
    return {"message": f"Population record with id {pop_id} successfully deleted"}
