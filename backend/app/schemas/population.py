"""Pydantic schemas for Population CRUD operations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PopulationBase(BaseModel):
    location_name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Ward 4 Riverside Zone"})
    total_population: int = Field(..., gt=0, json_schema_extra={"example": 12500})
    vulnerable_population: int = Field(0, ge=0, json_schema_extra={"example": 2100})
    density_per_sq_km: float = Field(0.0, ge=0.0, json_schema_extra={"example": 4500.0})
    location_id: Optional[int] = None


class PopulationCreate(PopulationBase):
    pass


class PopulationUpdate(BaseModel):
    location_name: Optional[str] = Field(None, min_length=2, max_length=255)
    total_population: Optional[int] = Field(None, gt=0)
    vulnerable_population: Optional[int] = Field(None, ge=0)
    density_per_sq_km: Optional[float] = Field(None, ge=0.0)
    location_id: Optional[int] = None


class PopulationResponse(PopulationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
