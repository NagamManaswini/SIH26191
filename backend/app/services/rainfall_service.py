"""Service layer for Rainfall Record database operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.entities import RainfallRecord
from backend.app.schemas.rainfall import RainfallRecordCreate, RainfallRecordUpdate, RainfallRecordResponse
from backend.app.utils.geo import coords_to_point_wkt, point_wkt_to_coords


def _rainfall_to_response(record: RainfallRecord) -> RainfallRecordResponse:
    coords = point_wkt_to_coords(record.station_location) if record.station_location else None
    lat = coords[1] if coords else None
    lon = coords[0] if coords else None

    return RainfallRecordResponse(
        id=record.id,
        location_name=record.location_name,
        rainfall_mm=record.rainfall_mm,
        duration_hours=record.duration_hours,
        intensity=record.intensity,
        latitude=lat,
        longitude=lon,
        recorded_at=record.recorded_at,
    )


def create_rainfall_record(db: Session, record_in: RainfallRecordCreate) -> RainfallRecordResponse:
    station_wkt = None
    if record_in.latitude is not None and record_in.longitude is not None:
        station_wkt = coords_to_point_wkt(record_in.longitude, record_in.latitude)

    db_record = RainfallRecord(
        location_name=record_in.location_name,
        rainfall_mm=record_in.rainfall_mm,
        duration_hours=record_in.duration_hours,
        intensity=record_in.intensity,
        station_location=station_wkt,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return _rainfall_to_response(db_record)


def get_rainfall_records(db: Session, skip: int = 0, limit: int = 100) -> List[RainfallRecordResponse]:
    records = db.query(RainfallRecord).offset(skip).limit(limit).all()
    return [_rainfall_to_response(r) for r in records]


def get_rainfall_record_by_id(db: Session, record_id: int) -> RainfallRecordResponse:
    record = db.query(RainfallRecord).filter(RainfallRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rainfall record with id {record_id} not found",
        )
    return _rainfall_to_response(record)


def update_rainfall_record(db: Session, record_id: int, record_in: RainfallRecordUpdate) -> RainfallRecordResponse:
    record = db.query(RainfallRecord).filter(RainfallRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rainfall record with id {record_id} not found",
        )

    update_data = record_in.model_dump(exclude_unset=True)
    lat = update_data.pop("latitude", None)
    lon = update_data.pop("longitude", None)
    if lat is not None and lon is not None:
        record.station_location = coords_to_point_wkt(lon, lat)

    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return _rainfall_to_response(record)


def delete_rainfall_record(db: Session, record_id: int) -> dict:
    record = db.query(RainfallRecord).filter(RainfallRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rainfall record with id {record_id} not found",
        )
    db.delete(record)
    db.commit()
    return {"message": f"Rainfall record with id {record_id} successfully deleted"}
