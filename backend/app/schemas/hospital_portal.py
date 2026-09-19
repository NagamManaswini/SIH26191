"""Pydantic schemas for the Hospital Portal (hospital self-service endpoints)."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ---------------------------------------------
# Hospital Profile
# ---------------------------------------------

class HospitalProfileOut(BaseModel):
    id: int
    hospital_id: str
    name: str
    type: str
    address: Optional[str]
    district: Optional[str]
    state: Optional[str]
    latitude: float
    longitude: float
    phone: Optional[str]
    emergency_status: str
    operational_status: str
    specialization: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class HospitalProfileUpdate(BaseModel):
    """Fields a hospital user is PERMITTED to update on their own profile."""
    phone: Optional[str] = None
    specialization: Optional[str] = None
    # Note: name, hospital_id, latitude, longitude, district, state, type cannot be changed by hospital


# ---------------------------------------------
# Capacity
# ---------------------------------------------

class HospitalCapacityUpdatePortal(BaseModel):
    """Hospital-user capacity update schema."""
    total_beds: Optional[int] = Field(None, ge=0)
    occupied_beds: Optional[int] = Field(None, ge=0)
    total_icu: Optional[int] = Field(None, ge=0)
    occupied_icu: Optional[int] = Field(None, ge=0)
    total_emergency_beds: Optional[int] = Field(None, ge=0)
    occupied_emergency_beds: Optional[int] = Field(None, ge=0)
    isolation_beds: Optional[int] = Field(None, ge=0)
    total_ambulances: Optional[int] = Field(None, ge=0)
    available_ambulances: Optional[int] = Field(None, ge=0)


class HospitalCapacityOut(BaseModel):
    id: int
    hospital_id: int
    total_beds: int
    occupied_beds: int
    available_beds: int
    total_icu: int
    occupied_icu: int
    available_icu: int
    total_emergency_beds: int
    occupied_emergency_beds: int
    available_emergency_beds: int
    isolation_beds: int
    total_ambulances: int
    available_ambulances: int
    busy_ambulances: int
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    class Config:
        orm_mode = True


# ---------------------------------------------
# Operational Status
# ---------------------------------------------

class HospitalStatusUpdate(BaseModel):
    status: str  # OPEN, LIMITED, FULL, EMERGENCY_ONLY, CLOSED
    reason: Optional[str] = None


class HospitalStatusHistoryOut(BaseModel):
    id: int
    hospital_id: int
    old_status: Optional[str]
    new_status: str
    updated_by: str
    updated_by_role: str
    reason: Optional[str]
    updated_at: datetime

    class Config:
        orm_mode = True


# ---------------------------------------------
# Emergency Requests
# ---------------------------------------------

class EmergencyRequestCreate(BaseModel):
    """Used by Field Operator / Admin to create an ER request targeting a hospital."""
    hospital_id: int
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    patients_count: int = Field(1, ge=1)
    medical_requirement: str = "Emergency Treatment"
    priority: str = "HIGH"
    distance_km: float = 0.0
    estimated_arrival_minutes: float = 0.0
    notes: Optional[str] = None


class EmergencyRequestStatusUpdate(BaseModel):
    """Hospital updates the status of an incoming request."""
    status: str  # ACCEPTED, REJECTED, IN_PROGRESS, COMPLETED
    notes: Optional[str] = None


class EmergencyRequestOut(BaseModel):
    id: int
    request_code: str
    hospital_id: int
    location_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    patients_count: int
    medical_requirement: str
    priority: str
    distance_km: float
    estimated_arrival_minutes: float
    status: str
    created_by: str
    created_by_role: str
    notes: Optional[str]
    responded_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


# ---------------------------------------------
# Patients
# ---------------------------------------------

class HospitalPatientCreate(BaseModel):
    emergency_request_id: Optional[int] = None
    age_range: Optional[str] = None
    medical_priority: str = "MEDIUM"
    assigned_department: Optional[str] = None


class HospitalPatientStatusUpdate(BaseModel):
    treatment_status: Optional[str] = None
    discharge_status: Optional[str] = None
    assigned_department: Optional[str] = None


class HospitalPatientOut(BaseModel):
    id: int
    patient_code: str
    emergency_request_id: Optional[int]
    hospital_id: int
    age_range: Optional[str]
    medical_priority: str
    arrival_time: Optional[datetime]
    treatment_status: str
    assigned_department: Optional[str]
    discharge_status: str
    discharge_time: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


# ---------------------------------------------
# Analytics
# ---------------------------------------------

class HospitalAnalyticsOut(BaseModel):
    hospital_id: int
    hospital_name: str
    operational_status: str
    bed_utilization_pct: float
    icu_utilization_pct: float
    emergency_utilization_pct: float
    ambulance_availability_pct: float
    total_emergency_requests_today: int
    accepted_requests_today: int
    rejected_requests_today: int
    pending_requests: int
    active_patients: int
    last_capacity_update: Optional[datetime]
