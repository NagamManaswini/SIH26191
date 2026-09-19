"""Service layer for Hazard Zone database operations."""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from shapely.geometry import Polygon, mapping
from shapely.wkt import loads as wkt_loads, dumps as wkt_dumps

from backend.app.models.entities import HazardZone
from backend.app.schemas.hazard_zone import HazardZoneCreate, HazardZoneUpdate, HazardZoneResponse


def _coords_to_polygon_wkt(coordinates: List[List[List[float]]]) -> str:
    """Convert GeoJSON polygon coordinates to WKT string."""
    try:
        shell = coordinates[0]
        holes = coordinates[1:] if len(coordinates) > 1 else None
        poly = Polygon(shell, holes)
        return wkt_dumps(poly)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid polygon coordinates format: {str(e)}",
        )


def _polygon_wkt_to_coords(wkt_str: str) -> List[List[List[float]]]:
    """Convert WKT string back to GeoJSON coordinates format."""
    if not wkt_str:
        return []
    try:
        geom = wkt_loads(str(wkt_str))
        geojson = mapping(geom)
        return geojson.get("coordinates", [])
    except Exception:
        return []


def _hazard_to_response(hazard: HazardZone) -> HazardZoneResponse:
    coords = _polygon_wkt_to_coords(hazard.boundary)
    return HazardZoneResponse(
        id=hazard.id,
        name=hazard.name,
        hazard_type=hazard.hazard_type,
        risk_level=hazard.risk_level,
        risk_score=hazard.risk_score,
        coordinates=coords,
        created_at=hazard.created_at,
        updated_at=hazard.updated_at,
    )


def create_hazard_zone(db: Session, hazard_in: HazardZoneCreate) -> HazardZoneResponse:
    wkt_boundary = _coords_to_polygon_wkt(hazard_in.coordinates)
    db_hazard = HazardZone(
        name=hazard_in.name,
        hazard_type=hazard_in.hazard_type,
        risk_level=hazard_in.risk_level.upper(),
        risk_score=hazard_in.risk_score,
        boundary=wkt_boundary,
    )
    db.add(db_hazard)
    db.commit()
    db.refresh(db_hazard)
    return _hazard_to_response(db_hazard)


def get_hazard_zones(
    db: Session, skip: int = 0, limit: int = 100, risk_level: Optional[str] = None
) -> List[HazardZoneResponse]:
    query = db.query(HazardZone)
    if risk_level:
        query = query.filter(HazardZone.risk_level == risk_level.upper())
    hazards = query.offset(skip).limit(limit).all()
    return [_hazard_to_response(h) for h in hazards]


def get_hazard_zone_by_id(db: Session, hazard_id: int) -> HazardZoneResponse:
    hazard = db.query(HazardZone).filter(HazardZone.id == hazard_id).first()
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard zone with id {hazard_id} not found",
        )
    return _hazard_to_response(hazard)


def update_hazard_zone(db: Session, hazard_id: int, hazard_in: HazardZoneUpdate) -> HazardZoneResponse:
    hazard = db.query(HazardZone).filter(HazardZone.id == hazard_id).first()
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard zone with id {hazard_id} not found",
        )

    update_data = hazard_in.model_dump(exclude_unset=True)
    coords = update_data.pop("coordinates", None)
    if coords is not None:
        hazard.boundary = _coords_to_polygon_wkt(coords)

    if "risk_level" in update_data and update_data["risk_level"]:
        update_data["risk_level"] = update_data["risk_level"].upper()

    for field, value in update_data.items():
        setattr(hazard, field, value)

    db.commit()
    db.refresh(hazard)
    return _hazard_to_response(hazard)


def delete_hazard_zone(db: Session, hazard_id: int) -> dict:
    hazard = db.query(HazardZone).filter(HazardZone.id == hazard_id).first()
    if not hazard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard zone with id {hazard_id} not found",
        )
    db.delete(hazard)
    db.commit()
    return {"message": f"Hazard zone with id {hazard_id} successfully deleted"}
