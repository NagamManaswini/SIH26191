"""Pydantic schemas for Rainfall Record CRUD operations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RainfallRecordBase(BaseModel):
    location_name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Station Alpha - Catchment 12"})
    rainfall_mm: float = Field(..., ge=0.0, json_schema_extra={"example": 185.5})
    duration_hours: float = Field(24.0, gt=0.0, json_schema_extra={"example": 12.0})
    intensity: str = Field("moderate", json_schema_extra={"example": "heavy"})  # light, moderate, heavy, extreme
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, json_schema_extra={"example": 19.0800})
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, json_schema_extra={"example": 72.8800})


class RainfallRecordCreate(RainfallRecordBase):
    pass


class RainfallRecordUpdate(BaseModel):
    location_name: Optional[str] = Field(None, min_length=2, max_length=255)
    rainfall_mm: Optional[float] = Field(None, ge=0.0)
    duration_hours: Optional[float] = Field(None, gt=0.0)
    intensity: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class RainfallRecordResponse(RainfallRecordBase):
    id: int
    recorded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
