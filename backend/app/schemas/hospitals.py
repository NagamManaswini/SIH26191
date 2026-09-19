"""Pydantic schemas for Dynamic Hospital Management and Emergency Response."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, root_validator


class HospitalCapacityBase(BaseModel):
    total_beds: int = Field(default=100, ge=0)
    occupied_beds: int = Field(default=0, ge=0)
    total_icu: int = Field(default=20, ge=0)
    occupied_icu: int = Field(default=0, ge=0)
    total_emergency_beds: int = Field(default=30, ge=0)
    occupied_emergency_beds: int = Field(default=0, ge=0)
    isolation_beds: int = Field(default=10, ge=0)
    total_ambulances: int = Field(default=5, ge=0)
    available_ambulances: int = Field(default=5, ge=0)

    @root_validator(skip_on_failure=True)
    def validate_occupancy_limits(cls, values):
        tot_beds = values.get("total_beds", 100)
        occ_beds = values.get("occupied_beds", 0)
        if occ_beds > tot_beds:
            raise ValueError(f"Occupied beds ({occ_beds}) cannot exceed total beds ({tot_beds})")

        tot_icu = values.get("total_icu", 20)
        occ_icu = values.get("occupied_icu", 0)
        if occ_icu > tot_icu:
            raise ValueError(f"Occupied ICU beds ({occ_icu}) cannot exceed total ICU beds ({tot_icu})")

        tot_em = values.get("total_emergency_beds", 30)
        occ_em = values.get("occupied_emergency_beds", 0)
        if occ_em > tot_em:
            raise ValueError(f"Occupied emergency beds ({occ_em}) cannot exceed total emergency beds ({tot_em})")

        tot_amb = values.get("total_ambulances", 5)
        avail_amb = values.get("available_ambulances", 5)
        if avail_amb > tot_amb:
            raise ValueError(f"Available ambulances ({avail_amb}) cannot exceed total ambulances ({tot_amb})")

        return values


class HospitalCapacityCreate(HospitalCapacityBase):
    pass


class HospitalCapacityUpdate(BaseModel):
    total_beds: Optional[int] = Field(None, ge=0)
    occupied_beds: Optional[int] = Field(None, ge=0)
    total_icu: Optional[int] = Field(None, ge=0)
    occupied_icu: Optional[int] = Field(None, ge=0)
    total_emergency_beds: Optional[int] = Field(None, ge=0)
    occupied_emergency_beds: Optional[int] = Field(None, ge=0)
    isolation_beds: Optional[int] = Field(None, ge=0)
    total_ambulances: Optional[int] = Field(None, ge=0)
    available_ambulances: Optional[int] = Field(None, ge=0)
    updated_by: Optional[str] = "Admin"


class HospitalCapacityOut(HospitalCapacityBase):
    id: int
    hospital_id: int
    available_beds: int
    available_icu: int
    available_emergency_beds: int
    busy_ambulances: int
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    class Config:
        orm_mode = True


class HospitalUpdateAuditOut(BaseModel):
    id: int
    hospital_id: int
    field_name: str
    old_value: Optional[str]
    new_value: str
    updated_by: str
    timestamp: datetime

    class Config:
        orm_mode = True


class HospitalBase(BaseModel):
    hospital_id: str
    name: str
    type: str = "Government"
    address: Optional[str] = None
    latitude: float
    longitude: float
    district: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    emergency_status: str = "OPEN"  # OPEN, LIMITED, FULL, EMERGENCY_ONLY, CLOSED, UNKNOWN
    operational_status: str = "OPEN"  # OPEN, LIMITED, FULL, EMERGENCY_ONLY, CLOSED, UNKNOWN
    specialization: Optional[str] = "General & Trauma Response"
    data_source: str = "Hospital Management System"
    is_active: bool = True


class HospitalCreate(HospitalBase):
    capacity: Optional[HospitalCapacityCreate] = None


class HospitalUpdateSchema(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    district: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    emergency_status: Optional[str] = None
    operational_status: Optional[str] = None
    specialization: Optional[str] = None
    data_source: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[str] = "Admin"


class HospitalOut(HospitalBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    capacity: Optional[HospitalCapacityOut] = None

    class Config:
        orm_mode = True


class HospitalRecommendationRequest(BaseModel):
    latitude: float
    longitude: float
    medical_need: str = "emergency"  # emergency, icu, general, trauma
    patients: int = 1
    required_specialization: Optional[str] = None
    max_radius_km: float = 50.0


class RecommendedHospitalItem(BaseModel):
    id: int
    hospital_id: str
    name: str
    type: str
    address: Optional[str]
    latitude: float
    longitude: float
    district: Optional[str]
    phone: Optional[str]
    emergency_status: str
    operational_status: str
    specialization: Optional[str]
    distance_km: float
    estimated_travel_minutes: float
    available_emergency_beds: int
    available_icu: int
    available_beds: int
    available_ambulances: int
    status: str
    score: float


class HospitalRecommendationResponse(BaseModel):
    recommended_hospital: Optional[RecommendedHospitalItem] = None
    alternatives: List[RecommendedHospitalItem] = []
    message: str = "Success"
