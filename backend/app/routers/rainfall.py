from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.rainfall import RainfallRecordCreate, RainfallRecordUpdate, RainfallRecordResponse
from backend.app.services.rainfall_service import (
    create_rainfall_record,
    get_rainfall_records,
    get_rainfall_record_by_id,
    update_rainfall_record,
    delete_rainfall_record,
)

router = APIRouter(prefix="/rainfall-records", tags=["Rainfall Records"])


@router.post("", response_model=RainfallRecordResponse, status_code=status.HTTP_201_CREATED)
def create_new_rainfall_record(record_in: RainfallRecordCreate, db: Session = Depends(get_db)):
    """Create a new rainfall observation record."""
    return create_rainfall_record(db=db, record_in=record_in)


@router.get("", response_model=List[RainfallRecordResponse])
def list_rainfall_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Retrieve list of rainfall records."""
    return get_rainfall_records(db=db, skip=skip, limit=limit)


@router.get("/{record_id}", response_model=RainfallRecordResponse)
def get_rainfall_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific rainfall record by ID."""
    return get_rainfall_record_by_id(db=db, record_id=record_id)


@router.put("/{record_id}", response_model=RainfallRecordResponse)
def update_existing_rainfall_record(
    record_id: int, record_in: RainfallRecordUpdate, db: Session = Depends(get_db)
):
    """Update a rainfall record."""
    return update_rainfall_record(db=db, record_id=record_id, record_in=record_in)


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
def remove_rainfall_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a rainfall record."""
    return delete_rainfall_record(db=db, record_id=record_id)
