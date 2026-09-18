from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud.crud_watershed import watershed_crud
from app.schemas.watershed import WatershedRead

router = APIRouter(prefix="/watersheds", tags=["Watersheds"])

@router.get("", response_model=List[WatershedRead])
def list_watersheds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    List all micro-watershed catchment polygons and risk attributes.
    """
    return watershed_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{watershed_id}", response_model=WatershedRead)
def get_watershed(watershed_id: int, db: Session = Depends(get_db)):
    """
    Get watershed by primary key ID.
    """
    watershed = watershed_crud.get(db, id=watershed_id)
    if not watershed:
        raise HTTPException(status_code=404, detail="Watershed not found")
    return watershed
