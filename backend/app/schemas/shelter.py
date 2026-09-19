"""Pydantic schemas for Shelter CRUD & Capacity Assessment operations."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ShelterBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Central Government High School Shelter"})
    address: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Main Street, District 1"})
    capacity: int = Field(..., gt=0, json_schema_extra={"example": 500})
    current_occupancy: int = Field(0, ge=0, json_schema_extra={"example": 50})
    status: str = Field("active", json_schema_extra={"example": "active"})  # active, full, inactive, maintenance
    contact_number: Optional[str] = Field(None, max_length=50, json_schema_extra={"example": "+91 9876543210"})
    accessibility_rating: float = Field(0.8, ge=0.0, le=1.0, json_schema_extra={"example": 0.85})
    structural_safety_rating: float = Field(0.9, ge=0.0, le=1.0, json_schema_extra={"example": 0.95})
    latitude: float = Field(..., ge=-90.0, le=90.0, json_schema_extra={"example": 19.0760})
    longitude: float = Field(..., ge=-180.0, le=180.0, json_schema_extra={"example": 72.8777})


class ShelterCreate(ShelterBase):
    pass


class ShelterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    address: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    current_occupancy: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    contact_number: Optional[str] = None
    accessibility_rating: Optional[float] = Field(None, ge=0.0, le=1.0)
    structural_safety_rating: Optional[float] = Field(None, ge=0.0, le=1.0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class ShelterResponse(ShelterBase):
    id: int
    available_capacity: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ShelterCapacityMetricsResponse(BaseModel):
    id: int
    name: str
    maximum_capacity: int
    current_occupancy: int
    available_capacity: int
    occupancy_percentage: float
    resource_score: float
    accessibility_score: float
    safety_score: float
    overall_suitability: float
    can_accept_evacuees: bool
    status: str
    latitude: float
    longitude: float
    resources_breakdown: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ShelterEvaluateRequest(BaseModel):
    evacuee_count: int = Field(..., gt=0, json_schema_extra={"example": 120})
    origin_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, json_schema_extra={"example": 19.0800})
    origin_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, json_schema_extra={"example": 72.8800})
    max_distance_km: float = Field(25.0, gt=0.0, json_schema_extra={"example": 25.0})


class ShelterEvaluateResponse(BaseModel):
    evacuee_count: int
    assigned_shelter_id: Optional[int] = None
    assigned_shelter_name: Optional[str] = None
    is_assignment_possible: bool
    message: str
    suitable_shelters: List[ShelterCapacityMetricsResponse]
