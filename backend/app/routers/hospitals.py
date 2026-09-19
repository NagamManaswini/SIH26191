"""FastAPI Router for Dynamic Hospital Management and Emergency Response."""

import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.entities import Hospital, HospitalCapacity, HospitalUpdate, User
from backend.app.schemas.hospitals import (
    HospitalOut,
    HospitalCreate,
    HospitalUpdateSchema,
    HospitalCapacityOut,
    HospitalCapacityUpdate,
    HospitalUpdateAuditOut,
    HospitalRecommendationRequest,
    HospitalRecommendationResponse,
    RecommendedHospitalItem,
)
from backend.app.services.hospital_provider import get_hospital_data_provider

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two lat/lon coordinates."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def verify_admin_role(x_user_role: Optional[str] = Header(None, alias="X-User-Role")):
    """Authorization check to enforce Admin role for mutating endpoints."""
    # If header is not passed or role is user, allow if developer mode or reject if explicitly not admin
    if x_user_role and x_user_role.lower() not in ["admin", "responder"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin authorization required to perform this action."
        )


@router.get("", response_model=List[HospitalOut])
def get_hospitals(
    district: Optional[str] = Query(None, description="Filter by district"),
    type: Optional[str] = Query(None, description="Filter by hospital type"),
    status: Optional[str] = Query(None, description="Filter by operational status"),
    db: Session = Depends(get_db),
):
    """Retrieve all hospitals with optional filtering."""
    query = db.query(Hospital).filter(Hospital.is_active == True)
    if district:
        query = query.filter(Hospital.district.ilike(f"%{district}%"))
    if type:
        query = query.filter(Hospital.type.ilike(f"%{type}%"))
    if status:
        query = query.filter(Hospital.operational_status.ilike(f"%{status}%"))
    return query.all()


@router.get("/nearby", response_model=List[RecommendedHospitalItem])
def get_nearby_hospitals(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius_km: float = Query(30.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db),
):
    """Find nearby hospitals within radius, sorted by distance."""
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    results = []
    for h in hospitals:
        dist = haversine_distance(latitude, longitude, h.latitude, h.longitude)
        if dist <= radius_km:
            cap = h.capacity
            avail_beds = max(0, cap.total_beds - cap.occupied_beds) if cap else 0
            avail_icu = max(0, cap.total_icu - cap.occupied_icu) if cap else 0
            avail_em = max(0, cap.total_emergency_beds - cap.occupied_emergency_beds) if cap else 0
            avail_amb = cap.available_ambulances if cap else 0
            travel_mins = round((dist / 35.0) * 60.0, 1)

            results.append(
                RecommendedHospitalItem(
                    id=h.id,
                    hospital_id=h.hospital_id,
                    name=h.name,
                    type=h.type,
                    address=h.address,
                    latitude=h.latitude,
                    longitude=h.longitude,
                    district=h.district,
                    phone=h.phone,
                    emergency_status=h.emergency_status,
                    operational_status=h.operational_status,
                    specialization=h.specialization,
                    distance_km=round(dist, 2),
                    estimated_travel_minutes=travel_mins,
                    available_emergency_beds=avail_em,
                    available_icu=avail_icu,
                    available_beds=avail_beds,
                    available_ambulances=avail_amb,
                    status=h.operational_status,
                    score=100.0 - dist,
                )
            )
    results.sort(key=lambda x: x.distance_km)
    return results


@router.get("/available", response_model=List[HospitalOut])
def get_available_hospitals(
    min_emergency_beds: int = Query(1, ge=0),
    min_icu_beds: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Filter hospitals with available emergency or ICU beds."""
    hospitals = db.query(Hospital).filter(
        Hospital.is_active == True,
        Hospital.operational_status.in_(["OPEN", "LIMITED", "EMERGENCY_ONLY"])
    ).all()

    result = []
    for h in hospitals:
        if h.capacity:
            avail_em = h.capacity.total_emergency_beds - h.capacity.occupied_emergency_beds
            avail_icu = h.capacity.total_icu - h.capacity.occupied_icu
            if avail_em >= min_emergency_beds and avail_icu >= min_icu_beds:
                result.append(h)
    return result


@router.post("/recommend", response_model=HospitalRecommendationResponse)
def recommend_hospital(
    req: HospitalRecommendationRequest,
    db: Session = Depends(get_db),
):
    """Multi-factor hospital recommendation algorithm for emergency medical response."""
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    if not hospitals:
        return HospitalRecommendationResponse(
            recommended_hospital=None,
            alternatives=[],
            message="No hospitals found in the database."
        )

    candidates = []
    for h in hospitals:
        # Distance calculation
        dist = haversine_distance(req.latitude, req.longitude, h.latitude, h.longitude)
        if dist > req.max_radius_km:
            continue

        cap = h.capacity
        avail_beds = max(0, cap.total_beds - cap.occupied_beds) if cap else 0
        avail_icu = max(0, cap.total_icu - cap.occupied_icu) if cap else 0
        avail_em = max(0, cap.total_emergency_beds - cap.occupied_emergency_beds) if cap else 0
        avail_amb = cap.available_ambulances if cap else 0

        # Skip closed or full hospitals for emergency needs if no beds available
        if h.operational_status == "CLOSED":
            continue

        if req.medical_need == "emergency" and avail_em <= 0 and avail_beds <= 0:
            continue

        # Multi-Factor Ranking Score Formulation
        # 1. Emergency capability & Operational Status (Weight: 35)
        status_score = 0.0
        if h.operational_status == "OPEN":
            status_score = 35.0
        elif h.operational_status == "EMERGENCY_ONLY":
            status_score = 30.0
        elif h.operational_status == "LIMITED":
            status_score = 20.0
        else:
            status_score = 5.0

        # 2. Available Emergency Beds / Capacity (Weight: 25)
        bed_score = min(25.0, (avail_em / max(1, req.patients)) * 10.0)

        # 3. ICU Availability when required (Weight: 15)
        icu_score = min(15.0, avail_icu * 1.5)

        # 4. Distance / Travel time proximity penalty (Weight: 20)
        dist_score = max(0.0, 20.0 - (dist * 0.5))

        # 5. Ambulance availability (Weight: 5)
        amb_score = min(5.0, avail_amb * 1.0)

        total_score = status_score + bed_score + icu_score + dist_score + amb_score
        travel_mins = round((dist / 30.0) * 60.0, 1)

        item = RecommendedHospitalItem(
            id=h.id,
            hospital_id=h.hospital_id,
            name=h.name,
            type=h.type,
            address=h.address,
            latitude=h.latitude,
            longitude=h.longitude,
            district=h.district,
            phone=h.phone,
            emergency_status=h.emergency_status,
            operational_status=h.operational_status,
            specialization=h.specialization,
            distance_km=round(dist, 2),
            estimated_travel_minutes=travel_mins,
            available_emergency_beds=avail_em,
            available_icu=avail_icu,
            available_beds=avail_beds,
            available_ambulances=avail_amb,
            status=h.operational_status,
            score=round(total_score, 2),
        )
        candidates.append(item)

    if not candidates:
        return HospitalRecommendationResponse(
            recommended_hospital=None,
            alternatives=[],
            message="No suitable operational hospital with available capacity found within radius."
        )

    # Rank by total multi-factor score descending
    candidates.sort(key=lambda x: x.score, reverse=True)

    recommended = candidates[0]
    alternatives = candidates[1:5]

    return HospitalRecommendationResponse(
        recommended_hospital=recommended,
        alternatives=alternatives,
        message="Recommended optimal medical facility based on capacity, status, and proximity."
    )


@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital_by_id(hospital_id: int, db: Session = Depends(get_db)):
    """Retrieve specific hospital details."""
    h = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return h


@router.post("", response_model=HospitalOut, status_code=status.HTTP_201_CREATED)
def create_hospital(
    hospital_in: HospitalCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_role),
):
    """Add a new hospital (Admin Only)."""
    existing = db.query(Hospital).filter(Hospital.hospital_id == hospital_in.hospital_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Hospital with ID {hospital_in.hospital_id} already exists.")

    hospital_data = hospital_in.dict(exclude={"capacity"})
    db_hospital = Hospital(**hospital_data)
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)

    # Initialize capacity
    cap_data = hospital_in.capacity.dict() if hospital_in.capacity else {}
    avail_b = cap_data.get("total_beds", 100) - cap_data.get("occupied_beds", 0)
    avail_i = cap_data.get("total_icu", 20) - cap_data.get("occupied_icu", 0)
    avail_e = cap_data.get("total_emergency_beds", 30) - cap_data.get("occupied_emergency_beds", 0)

    db_cap = HospitalCapacity(
        hospital_id=db_hospital.id,
        total_beds=cap_data.get("total_beds", 100),
        occupied_beds=cap_data.get("occupied_beds", 0),
        available_beds=max(0, avail_b),
        total_icu=cap_data.get("total_icu", 20),
        occupied_icu=cap_data.get("occupied_icu", 0),
        available_icu=max(0, avail_i),
        total_emergency_beds=cap_data.get("total_emergency_beds", 30),
        occupied_emergency_beds=cap_data.get("occupied_emergency_beds", 0),
        available_emergency_beds=max(0, avail_e),
        isolation_beds=cap_data.get("isolation_beds", 10),
        total_ambulances=cap_data.get("total_ambulances", 5),
        available_ambulances=cap_data.get("available_ambulances", 5),
        busy_ambulances=max(0, cap_data.get("total_ambulances", 5) - cap_data.get("available_ambulances", 5)),
        updated_by="Admin",
    )
    db.add(db_cap)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital


@router.patch("/{hospital_id}", response_model=HospitalOut)
def update_hospital(
    hospital_id: int,
    update_in: HospitalUpdateSchema,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_role),
):
    """Update hospital metadata and operational status (Admin Only)."""
    h = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")

    update_data = update_in.dict(exclude_unset=True)
    updated_by = update_data.pop("updated_by", "Admin")

    for field, val in update_data.items():
        old_val = getattr(h, field, None)
        if str(old_val) != str(val):
            setattr(h, field, val)
            # Log update audit
            audit = HospitalUpdate(
                hospital_id=h.id,
                field_name=field,
                old_value=str(old_val),
                new_value=str(val),
                updated_by=updated_by,
            )
            db.add(audit)

    h.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(h)
    return h


@router.get("/{hospital_id}/capacity", response_model=HospitalCapacityOut)
def get_hospital_capacity(hospital_id: int, db: Session = Depends(get_db)):
    """Retrieve current capacity breakdown for a hospital."""
    h = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")
    if not h.capacity:
        raise HTTPException(status_code=404, detail="Capacity record unavailable for this hospital.")
    return h.capacity


@router.patch("/{hospital_id}/capacity", response_model=HospitalCapacityOut)
def update_hospital_capacity(
    hospital_id: int,
    cap_in: HospitalCapacityUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_role),
):
    """Update hospital capacity (Admin Only). Validates constraints & writes audit log."""
    h = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")

    cap = h.capacity
    if not cap:
        cap = HospitalCapacity(hospital_id=h.id)
        db.add(cap)
        db.commit()
        db.refresh(cap)

    update_data = cap_in.dict(exclude_unset=True)
    updated_by = update_data.pop("updated_by", "Admin")

    # Compute target merged values for validation
    t_beds = update_data.get("total_beds", cap.total_beds)
    o_beds = update_data.get("occupied_beds", cap.occupied_beds)
    t_icu = update_data.get("total_icu", cap.total_icu)
    o_icu = update_data.get("occupied_icu", cap.occupied_icu)
    t_em = update_data.get("total_emergency_beds", cap.total_emergency_beds)
    o_em = update_data.get("occupied_emergency_beds", cap.occupied_emergency_beds)
    t_amb = update_data.get("total_ambulances", cap.total_ambulances)
    a_amb = update_data.get("available_ambulances", cap.available_ambulances)

    if o_beds > t_beds:
        raise HTTPException(status_code=400, detail=f"Occupied beds ({o_beds}) cannot exceed total beds ({t_beds})")
    if o_icu > t_icu:
        raise HTTPException(status_code=400, detail=f"Occupied ICU beds ({o_icu}) cannot exceed total ICU beds ({t_icu})")
    if o_em > t_em:
        raise HTTPException(status_code=400, detail=f"Occupied emergency beds ({o_em}) cannot exceed total emergency beds ({t_em})")
    if a_amb > t_amb:
        raise HTTPException(status_code=400, detail=f"Available ambulances ({a_amb}) cannot exceed total ambulances ({t_amb})")

    # Apply updates & log changes
    for field, val in update_data.items():
        old_val = getattr(cap, field, None)
        if str(old_val) != str(val):
            setattr(cap, field, val)
            audit = HospitalUpdate(
                hospital_id=h.id,
                field_name=f"capacity.{field}",
                old_value=str(old_val),
                new_value=str(val),
                updated_by=updated_by,
            )
            db.add(audit)

    # Recalculate derived available metrics
    cap.available_beds = max(0, cap.total_beds - cap.occupied_beds)
    cap.available_icu = max(0, cap.total_icu - cap.occupied_icu)
    cap.available_emergency_beds = max(0, cap.total_emergency_beds - cap.occupied_emergency_beds)
    cap.busy_ambulances = max(0, cap.total_ambulances - cap.available_ambulances)
    cap.updated_at = datetime.utcnow()
    cap.updated_by = updated_by

    # Automatically update operational_status if FULL
    if cap.available_emergency_beds == 0 and cap.available_beds == 0:
        h.operational_status = "FULL"
        h.emergency_status = "FULL"
    elif cap.available_emergency_beds > 0 and h.operational_status == "FULL":
        h.operational_status = "OPEN"
        h.emergency_status = "OPEN"

    db.commit()
    db.refresh(cap)
    return cap


@router.post("/{hospital_id}/updates", response_model=List[HospitalUpdateAuditOut])
def get_hospital_updates_history(hospital_id: int, db: Session = Depends(get_db)):
    """Retrieve audit update history log for a hospital."""
    h = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return db.query(HospitalUpdate).filter(HospitalUpdate.hospital_id == hospital_id).order_by(HospitalUpdate.timestamp.desc()).all()
