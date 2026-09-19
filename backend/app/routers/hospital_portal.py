"""FastAPI Router for Hospital Portal - Hospital self-service endpoints.
Uses X-User-Role + X-Hospital-Id header auth to match the existing system pattern.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
import uuid

from backend.app.database import get_db
from backend.app.models.entities import (
    Hospital, HospitalCapacity, HospitalUpdate, HospitalUser,
    EmergencyRequest, HospitalPatient, HospitalStatusHistory, Alert, User
)
from backend.app.schemas.hospital_portal import (
    HospitalProfileOut, HospitalProfileUpdate,
    HospitalCapacityUpdatePortal, HospitalCapacityOut,
    HospitalStatusUpdate, HospitalStatusHistoryOut,
    EmergencyRequestCreate, EmergencyRequestStatusUpdate, EmergencyRequestOut,
    HospitalPatientCreate, HospitalPatientStatusUpdate, HospitalPatientOut,
    HospitalAnalyticsOut,
)

router = APIRouter(prefix="/hospital", tags=["Hospital Portal"])


# ─────────────────────────────────────────────
# Auth Dependency — matches existing X-User-Role header pattern
# ─────────────────────────────────────────────

def get_hospital_context(
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_hospital_id: Optional[str] = Header(None, alias="X-Hospital-Id"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Validates that the request comes from a hospital user.
    Matches existing system pattern: X-User-Role: hospital, X-Hospital-Id: <id>
    """
    if not x_user_role or x_user_role.lower() != "hospital":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital role required. Pass X-User-Role: hospital header.",
        )

    hospital_id = None
    if x_hospital_id:
        try:
            hospital_id = int(x_hospital_id)
        except (ValueError, TypeError):
            pass

    if hospital_id is None:
        # Fallback: use the first available hospital for demo purposes
        hospital = db.query(Hospital).filter(Hospital.is_active == True).first()
    else:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id, Hospital.is_active == True).first()

    if not hospital:
        raise HTTPException(status_code=404, detail="Associated hospital not found.")

    return {
        "hospital": hospital,
        "hospital_id": hospital.id,
        "user_email": "hospital@ggh.example",
    }


def get_field_operator_context(
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
) -> Dict[str, Any]:
    """Admin or Field Operator can create ER requests."""
    if not x_user_role or x_user_role.lower() not in ["admin", "responder", "hospital"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Field Operator role required.",
        )
    return {"role": x_user_role.lower()}


# ─────────────────────────────────────────────
# Profile Endpoints
# ─────────────────────────────────────────────

@router.get("/me", response_model=HospitalProfileOut, summary="Get own hospital profile")
def get_hospital_me(ctx: Dict = Depends(get_hospital_context)):
    return ctx["hospital"]


@router.patch("/profile", response_model=HospitalProfileOut, summary="Update permitted profile fields")
def update_hospital_profile(
    update_in: HospitalProfileUpdate,
    ctx: Dict = Depends(get_hospital_context),
    db: Session = Depends(get_db),
):
    hospital = ctx["hospital"]
    update_data = update_in.dict(exclude_unset=True)
    allowed = {"phone", "specialization"}
    for field, val in update_data.items():
        if field in allowed:
            old_val = getattr(hospital, field, None)
            if str(old_val) != str(val):
                setattr(hospital, field, val)
                audit = HospitalUpdate(
                    hospital_id=hospital.id,
                    field_name=field,
                    old_value=str(old_val),
                    new_value=str(val),
                    updated_by=ctx["user_email"],
                )
                db.add(audit)
    hospital.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(hospital)
    return hospital


# ─────────────────────────────────────────────
# Capacity Endpoints
# ─────────────────────────────────────────────

@router.get("/capacity", response_model=HospitalCapacityOut, summary="Get own hospital capacity")
def get_hospital_capacity(ctx: Dict = Depends(get_hospital_context)):
    hospital = ctx["hospital"]
    if not hospital.capacity:
        raise HTTPException(status_code=404, detail="Capacity record not found.")
    return hospital.capacity


@router.patch("/capacity", response_model=HospitalCapacityOut, summary="Update own hospital capacity")
def update_hospital_capacity(
    cap_in: HospitalCapacityUpdatePortal,
    ctx: Dict = Depends(get_hospital_context),
    db: Session = Depends(get_db),
):
    hospital = ctx["hospital"]
    cap = hospital.capacity
    if not cap:
        cap = HospitalCapacity(hospital_id=hospital.id)
        db.add(cap)
        db.commit()
        db.refresh(cap)

    update_data = cap_in.dict(exclude_unset=True)
    t_beds = update_data.get("total_beds", cap.total_beds)
    o_beds = update_data.get("occupied_beds", cap.occupied_beds)
    t_icu = update_data.get("total_icu", cap.total_icu)
    o_icu = update_data.get("occupied_icu", cap.occupied_icu)
    t_em = update_data.get("total_emergency_beds", cap.total_emergency_beds)
    o_em = update_data.get("occupied_emergency_beds", cap.occupied_emergency_beds)
    t_amb = update_data.get("total_ambulances", cap.total_ambulances)
    a_amb = update_data.get("available_ambulances", cap.available_ambulances)

    if o_beds > t_beds:
        raise HTTPException(status_code=400, detail=f"Occupied beds ({o_beds}) cannot exceed total ({t_beds}).")
    if o_icu > t_icu:
        raise HTTPException(status_code=400, detail=f"Occupied ICU ({o_icu}) cannot exceed total ({t_icu}).")
    if o_em > t_em:
        raise HTTPException(status_code=400, detail=f"Occupied emergency beds ({o_em}) cannot exceed total ({t_em}).")
    if a_amb > t_amb:
        raise HTTPException(status_code=400, detail=f"Available ambulances ({a_amb}) cannot exceed total ({t_amb}).")

    for field, val in update_data.items():
        old_val = getattr(cap, field, None)
        if str(old_val) != str(val):
            setattr(cap, field, val)
            audit = HospitalUpdate(
                hospital_id=hospital.id,
                field_name=f"capacity.{field}",
                old_value=str(old_val),
                new_value=str(val),
                updated_by=ctx["user_email"],
            )
            db.add(audit)

    cap.available_beds = max(0, cap.total_beds - cap.occupied_beds)
    cap.available_icu = max(0, cap.total_icu - cap.occupied_icu)
    cap.available_emergency_beds = max(0, cap.total_emergency_beds - cap.occupied_emergency_beds)
    cap.busy_ambulances = max(0, cap.total_ambulances - cap.available_ambulances)
    cap.updated_at = datetime.now(timezone.utc)
    cap.updated_by = ctx["user_email"]

    # Auto update operational status if at full capacity
    if cap.available_emergency_beds == 0 and cap.available_beds == 0:
        old_status = hospital.operational_status
        hospital.operational_status = "FULL"
        hospital.emergency_status = "FULL"
        _log_status_change(db, hospital.id, old_status, "FULL", ctx["user_email"], "hospital", "Auto: capacity full")
    elif cap.available_emergency_beds > 0 and hospital.operational_status == "FULL":
        old_status = hospital.operational_status
        hospital.operational_status = "OPEN"
        hospital.emergency_status = "OPEN"
        _log_status_change(db, hospital.id, old_status, "OPEN", ctx["user_email"], "hospital", "Auto: capacity restored")

    db.commit()
    db.refresh(cap)
    return cap


# ─────────────────────────────────────────────
# Operational Status
# ─────────────────────────────────────────────

def _log_status_change(db, hospital_id, old_status, new_status, updated_by, updated_by_role, reason=None):
    entry = HospitalStatusHistory(
        hospital_id=hospital_id,
        old_status=old_status,
        new_status=new_status,
        updated_by=updated_by,
        updated_by_role=updated_by_role,
        reason=reason,
    )
    db.add(entry)


@router.patch("/status", response_model=HospitalProfileOut, summary="Update hospital operational status")
def update_hospital_status(
    status_in: HospitalStatusUpdate,
    ctx: Dict = Depends(get_hospital_context),
    db: Session = Depends(get_db),
):
    valid_statuses = {"OPEN", "LIMITED", "FULL", "EMERGENCY_ONLY", "CLOSED"}
    if status_in.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")
    hospital = ctx["hospital"]
    old_status = hospital.operational_status
    hospital.operational_status = status_in.status
    hospital.emergency_status = status_in.status
    hospital.updated_at = datetime.now(timezone.utc)
    _log_status_change(db, hospital.id, old_status, status_in.status, ctx["user_email"], "hospital", status_in.reason)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.get("/status/history", response_model=List[HospitalStatusHistoryOut], summary="Status history")
def get_status_history(ctx: Dict = Depends(get_hospital_context), db: Session = Depends(get_db)):
    hospital = ctx["hospital"]
    return db.query(HospitalStatusHistory).filter(
        HospitalStatusHistory.hospital_id == hospital.id
    ).order_by(HospitalStatusHistory.updated_at.desc()).limit(50).all()


# ─────────────────────────────────────────────
# Emergency Requests
# ─────────────────────────────────────────────

@router.get("/emergency-requests", response_model=List[EmergencyRequestOut], summary="Get incoming ER requests")
def get_emergency_requests(ctx: Dict = Depends(get_hospital_context), db: Session = Depends(get_db)):
    hospital = ctx["hospital"]
    return db.query(EmergencyRequest).filter(
        EmergencyRequest.hospital_id == hospital.id
    ).order_by(EmergencyRequest.created_at.desc()).all()


@router.patch("/emergency-requests/{request_id}", response_model=EmergencyRequestOut, summary="Update ER request status")
def update_emergency_request(
    request_id: int,
    update_in: EmergencyRequestStatusUpdate,
    ctx: Dict = Depends(get_hospital_context),
    db: Session = Depends(get_db),
):
    hospital = ctx["hospital"]
    req = db.query(EmergencyRequest).filter(EmergencyRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Emergency request not found.")
    if req.hospital_id != hospital.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Request belongs to another hospital.")
    valid_statuses = {"ACCEPTED", "REJECTED", "IN_PROGRESS", "COMPLETED"}
    if update_in.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")
    req.status = update_in.status
    if update_in.notes:
        req.notes = update_in.notes
    if update_in.status in {"ACCEPTED", "REJECTED"}:
        req.responded_at = datetime.now(timezone.utc)
    req.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    return req


@router.post("/emergency-requests", response_model=EmergencyRequestOut, status_code=status.HTTP_201_CREATED, summary="Create ER request")
def create_emergency_request(
    req_in: EmergencyRequestCreate,
    ctx: Dict = Depends(get_field_operator_context),
    db: Session = Depends(get_db),
):
    hospital = db.query(Hospital).filter(Hospital.id == req_in.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Target hospital not found.")
    request_code = f"ER-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    er = EmergencyRequest(
        request_code=request_code,
        hospital_id=req_in.hospital_id,
        location_name=req_in.location_name,
        latitude=req_in.latitude,
        longitude=req_in.longitude,
        patients_count=req_in.patients_count,
        medical_requirement=req_in.medical_requirement,
        priority=req_in.priority,
        distance_km=req_in.distance_km,
        estimated_arrival_minutes=req_in.estimated_arrival_minutes,
        notes=req_in.notes,
        created_by=f"{ctx['role']}_user",
        created_by_role=ctx["role"],
        status="PENDING",
    )
    db.add(er)
    db.commit()
    db.refresh(er)
    return er


# ─────────────────────────────────────────────
# Patients
# ─────────────────────────────────────────────

@router.get("/patients", response_model=List[HospitalPatientOut], summary="Get hospital patients")
def get_hospital_patients(ctx: Dict = Depends(get_hospital_context), db: Session = Depends(get_db)):
    hospital = ctx["hospital"]
    return db.query(HospitalPatient).filter(
        HospitalPatient.hospital_id == hospital.id
    ).order_by(HospitalPatient.arrival_time.desc()).all()


@router.post("/patients", response_model=HospitalPatientOut, status_code=status.HTTP_201_CREATED, summary="Admit a patient")
def create_patient(
    patient_in: HospitalPatientCreate,
    ctx: Dict = Depends(get_hospital_context),
    db: Session = Depends(get_db),
):
    hospital = ctx["hospital"]
    patient_code = f"PAT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    patient = HospitalPatient(
        patient_code=patient_code,
        emergency_request_id=patient_in.emergency_request_id,
        hospital_id=hospital.id,
        age_range=patient_in.age_range,
        medical_priority=patient_in.medical_priority,
        assigned_department=patient_in.assigned_department,
        treatment_status="ADMITTED",
        discharge_status="ACTIVE",
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.patch("/patients/{patient_id}", response_model=HospitalPatientOut, summary="Update patient status")
def update_patient(
    patient_id: int,
    update_in: HospitalPatientStatusUpdate,
    ctx: Dict = Depends(get_hospital_context),
    db: Session = Depends(get_db),
):
    hospital = ctx["hospital"]
    patient = db.query(HospitalPatient).filter(HospitalPatient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    if patient.hospital_id != hospital.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient belongs to another hospital.")
    update_data = update_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(patient, field, val)
    if update_in.discharge_status in {"DISCHARGED", "TRANSFERRED", "DECEASED"} and not patient.discharge_time:
        patient.discharge_time = datetime.now(timezone.utc)
    patient.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(patient)
    return patient


# ─────────────────────────────────────────────
# Alerts (filtered for hospital)
# ─────────────────────────────────────────────

@router.get("/alerts", summary="Get active alerts for this hospital")
def get_hospital_alerts(ctx: Dict = Depends(get_hospital_context), db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.status == "ACTIVE").order_by(Alert.created_time.desc()).limit(20).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "severity": a.severity,
            "affected_area": a.affected_area,
            "recommended_action": a.recommended_action,
            "status": a.status,
            "created_time": a.created_time,
        }
        for a in alerts
    ]


# ─────────────────────────────────────────────
# Analytics
# ─────────────────────────────────────────────

@router.get("/analytics", response_model=HospitalAnalyticsOut, summary="Get hospital analytics")
def get_hospital_analytics(ctx: Dict = Depends(get_hospital_context), db: Session = Depends(get_db)):
    hospital = ctx["hospital"]
    cap = hospital.capacity

    bed_util = icu_util = em_util = amb_avail = 0.0
    last_update = None

    if cap:
        bed_util = round((cap.occupied_beds / max(1, cap.total_beds)) * 100, 1)
        icu_util = round((cap.occupied_icu / max(1, cap.total_icu)) * 100, 1)
        em_util = round((cap.occupied_emergency_beds / max(1, cap.total_emergency_beds)) * 100, 1)
        amb_avail = round((cap.available_ambulances / max(1, cap.total_ambulances)) * 100, 1)
        last_update = cap.updated_at

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_requests = db.query(EmergencyRequest).filter(
        EmergencyRequest.hospital_id == hospital.id,
        EmergencyRequest.created_at >= today_start,
    ).all()
    accepted = sum(1 for r in today_requests if r.status == "ACCEPTED")
    rejected = sum(1 for r in today_requests if r.status == "REJECTED")
    pending = db.query(EmergencyRequest).filter(
        EmergencyRequest.hospital_id == hospital.id,
        EmergencyRequest.status == "PENDING",
    ).count()
    active_patients = db.query(HospitalPatient).filter(
        HospitalPatient.hospital_id == hospital.id,
        HospitalPatient.discharge_status == "ACTIVE",
    ).count()

    return HospitalAnalyticsOut(
        hospital_id=hospital.id,
        hospital_name=hospital.name,
        operational_status=hospital.operational_status,
        bed_utilization_pct=bed_util,
        icu_utilization_pct=icu_util,
        emergency_utilization_pct=em_util,
        ambulance_availability_pct=amb_avail,
        total_emergency_requests_today=len(today_requests),
        accepted_requests_today=accepted,
        rejected_requests_today=rejected,
        pending_requests=pending,
        active_patients=active_patients,
        last_capacity_update=last_update,
    )
