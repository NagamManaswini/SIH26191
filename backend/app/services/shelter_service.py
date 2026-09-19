"""Service layer for Shelter database operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.entities import Shelter
from backend.app.schemas.shelter import ShelterCreate, ShelterUpdate, ShelterResponse
from backend.app.utils.geo import coords_to_point_wkt, point_wkt_to_coords


def _shelter_to_response(shelter: Shelter) -> ShelterResponse:
    coords = point_wkt_to_coords(shelter.location)
    lat = coords[1] if coords else 0.0
    lon = coords[0] if coords else 0.0
    avail = max(0, shelter.capacity - shelter.current_occupancy)

    return ShelterResponse(
        id=shelter.id,
        name=shelter.name,
        address=shelter.address,
        capacity=shelter.capacity,
        current_occupancy=shelter.current_occupancy,
        available_capacity=avail,
        status=shelter.status,
        contact_number=shelter.contact_number,
        latitude=lat,
        longitude=lon,
        created_at=shelter.created_at,
        updated_at=shelter.updated_at,
    )


def create_shelter(db: Session, shelter_in: ShelterCreate) -> ShelterResponse:
    if shelter_in.current_occupancy > shelter_in.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current occupancy cannot exceed maximum shelter capacity.",
        )

    wkt_point = coords_to_point_wkt(shelter_in.longitude, shelter_in.latitude)
    db_shelter = Shelter(
        name=shelter_in.name,
        address=shelter_in.address,
        capacity=shelter_in.capacity,
        current_occupancy=shelter_in.current_occupancy,
        status=shelter_in.status,
        contact_number=shelter_in.contact_number,
        location=wkt_point,
    )
    db.add(db_shelter)
    db.commit()
    db.refresh(db_shelter)
    return _shelter_to_response(db_shelter)


def get_shelters(db: Session, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[ShelterResponse]:
    query = db.query(Shelter)
    if status_filter:
        query = query.filter(Shelter.status == status_filter)
    shelters = query.offset(skip).limit(limit).all()
    return [_shelter_to_response(s) for s in shelters]


def get_shelter_by_id(db: Session, shelter_id: int) -> ShelterResponse:
    shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
    if not shelter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shelter with id {shelter_id} not found",
        )
    return _shelter_to_response(shelter)


def update_shelter(db: Session, shelter_id: int, shelter_in: ShelterUpdate) -> ShelterResponse:
    shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
    if not shelter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shelter with id {shelter_id} not found",
        )

    update_data = shelter_in.model_dump(exclude_unset=True)
    
    # Check capacity vs occupancy rules if updating
    new_capacity = update_data.get("capacity", shelter.capacity)
    new_occupancy = update_data.get("current_occupancy", shelter.current_occupancy)
    if new_occupancy > new_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current occupancy cannot exceed maximum shelter capacity.",
        )

    lat = update_data.pop("latitude", None)
    lon = update_data.pop("longitude", None)
    if lat is not None and lon is not None:
        shelter.location = coords_to_point_wkt(lon, lat)

    for field, value in update_data.items():
        setattr(shelter, field, value)

    db.commit()
    db.refresh(shelter)
    return _shelter_to_response(shelter)


def delete_shelter(db: Session, shelter_id: int) -> dict:
    shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
    if not shelter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shelter with id {shelter_id} not found",
        )
    db.delete(shelter)
    db.commit()
    return {"message": f"Shelter with id {shelter_id} successfully deleted"}
