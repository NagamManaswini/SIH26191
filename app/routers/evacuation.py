"""
Evacuation Center Management and Safe Routing Router.

Provides endpoints for managing emergency shelters, discovering nearest
safe evacuation centers, and calculating hazard-avoiding evacuation routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.evacuation import EvacuationCenter
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.evacuation import (
    EvacuationCenterCreate,
    EvacuationCenterUpdate,
    EvacuationCenterRead,
    NearestCenterItem,
    EvacuationRouteResponse
)
from app.services.evacuation_routing_engine import evacuation_routing_engine
from app.core.deps import require_roles
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/evacuation", tags=["Evacuation Management & Safe Routing"])


def _format_center_read(c: EvacuationCenter) -> EvacuationCenterRead:
    avail = max(0, c.capacity - c.current_occupancy)
    occ_pct = round((c.current_occupancy / max(1, c.capacity)) * 100, 1)
    
    data = EvacuationCenterRead.model_validate(c)
    data.available_capacity = avail
    data.occupancy_percentage = occ_pct
    return data


@router.get("/centers", response_model=List[EvacuationCenterRead])
def get_evacuation_centers(
    is_active: Optional[bool] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all evacuation shelters with live capacity and occupancy metrics.
    """
    query = db.query(EvacuationCenter)
    if is_active is not None:
        query = query.filter(EvacuationCenter.is_active == is_active)
    if district:
        query = query.filter(EvacuationCenter.district == district)

    centers = query.order_by(desc(EvacuationCenter.capacity)).all()
    return [_format_center_read(c) for c in centers]


@router.post("/centers", response_model=EvacuationCenterRead, status_code=status.HTTP_201_CREATED)
async def create_evacuation_center(
    payload: EvacuationCenterCreate,
    current_user: User = Depends(require_roles([UserRole.GOVERNMENT_OFFICIAL, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Add a new disaster evacuation shelter.
    Restricted to Government Officials and Administrators.
    """
    center = EvacuationCenter(
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        capacity=payload.capacity,
        current_occupancy=payload.current_occupancy,
        is_active=payload.is_active,
        district=payload.district or "Rudraprayag",
        elevation_m=payload.elevation_m or 2100.0,
        contact_number=payload.contact_number,
        facilities=payload.facilities
    )
    db.add(center)
    db.commit()
    db.refresh(center)

    # Broadcast update
    await ws_manager.broadcast_json({
        "type": "EVACUATION_CENTER_CREATED",
        "data": {"id": center.id, "name": center.name, "capacity": center.capacity}
    })

    return _format_center_read(center)


@router.put("/centers/{center_id}", response_model=EvacuationCenterRead)
async def update_evacuation_center(
    center_id: int,
    payload: EvacuationCenterUpdate,
    current_user: User = Depends(require_roles([
        UserRole.GOVERNMENT_OFFICIAL,
        UserRole.ADMIN,
        UserRole.RESPONSE_TEAM
    ])),
    db: Session = Depends(get_db)
):
    """
    Update shelter capacity, live occupancy headcounts, or emergency activation status.
    Restricted to Government Officials, Admins, and Response Teams.
    """
    center = db.query(EvacuationCenter).filter(EvacuationCenter.id == center_id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Evacuation center not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(center, field, val)

    db.commit()
    db.refresh(center)

    # Broadcast update
    await ws_manager.broadcast_json({
        "type": "EVACUATION_CENTER_UPDATED",
        "data": {
            "id": center.id,
            "name": center.name,
            "current_occupancy": center.current_occupancy,
            "capacity": center.capacity,
            "is_active": center.is_active
        }
    })

    return _format_center_read(center)


@router.get("/nearest", response_model=List[NearestCenterItem])
def get_nearest_evacuation_centers(
    latitude: float = Query(..., description="Origin latitude coordinate"),
    longitude: float = Query(..., description="Origin longitude coordinate"),
    limit: int = Query(default=5, ge=1, le=20),
    only_available: bool = Query(default=True, description="Filter to only shelters with available capacity"),
    db: Session = Depends(get_db)
):
    """
    Find nearest safe evacuation shelters relative to current GPS position with capacity availability.
    """
    results = evacuation_routing_engine.find_nearest_safe_centers(
        db=db,
        latitude=latitude,
        longitude=longitude,
        limit=limit,
        only_available=only_available
    )
    return results


@router.get("/routes", response_model=EvacuationRouteResponse)
def get_safe_evacuation_route(
    origin_lat: float = Query(..., description="Starting latitude"),
    origin_lon: float = Query(..., description="Starting longitude"),
    destination_id: Optional[int] = Query(default=None, description="Optional target shelter ID (picks nearest safe if omitted)"),
    db: Session = Depends(get_db)
):
    """
    Calculates a hazard-avoiding safe evacuation route avoiding flood danger zones and road blockages.
    """
    if destination_id:
        center = db.query(EvacuationCenter).filter(EvacuationCenter.id == destination_id).first()
        if not center:
            raise HTTPException(status_code=404, detail="Destination evacuation center not found.")
    else:
        nearest = evacuation_routing_engine.find_nearest_safe_centers(
            db=db,
            latitude=origin_lat,
            longitude=origin_lon,
            limit=1,
            only_available=True
        )
        if not nearest:
            # Fallback to any active center
            center = db.query(EvacuationCenter).filter(EvacuationCenter.is_active == True).first()
            if not center:
                raise HTTPException(status_code=404, detail="No active evacuation centers available in region.")
        else:
            center = db.query(EvacuationCenter).filter(EvacuationCenter.id == nearest[0]["id"]).first()

    route_data = evacuation_routing_engine.calculate_safe_evacuation_route(
        db=db,
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        destination_center=center
    )
    return route_data
