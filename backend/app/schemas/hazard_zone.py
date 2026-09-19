"""Pydantic schemas for Hazard Zone CRUD & Analysis operations."""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class HazardZoneBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Hillside Landslide Red Zone A"})
    hazard_type: str = Field(..., json_schema_extra={"example": "landslide"})  # landslide, flood, cyclone, earthquake
    risk_level: str = Field(..., json_schema_extra={"example": "RED"})  # RED, YELLOW, GREEN, CRITICAL
    risk_score: float = Field(0.0, ge=0.0, le=1.0, json_schema_extra={"example": 0.85})
    # GeoJSON polygon coordinates list [[[lon, lat], [lon, lat], ...]]
    coordinates: List[List[List[float]]] = Field(
        ...,
        json_schema_extra={"example": [[[72.87, 19.07], [72.88, 19.07], [72.88, 19.08], [72.87, 19.08], [72.87, 19.07]]]}
    )


class HazardZoneCreate(HazardZoneBase):
    pass


class HazardZoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    hazard_type: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    coordinates: Optional[List[List[List[float]]]] = None


class HazardZoneResponse(HazardZoneBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HazardAnalyzeRequest(BaseModel):
    rainfall_mm: float = Field(150.0, ge=0.0, le=1000.0, json_schema_extra={"example": 180.0})
    region_name: str = Field("Western Hills Sector", json_schema_extra={"example": "Western Hills Sector"})
    weight_rainfall: float = Field(0.35, ge=0.0, le=1.0)
    weight_slope: float = Field(0.30, ge=0.0, le=1.0)
    threshold_low: float = Field(0.25, ge=0.0, le=1.0)
    threshold_moderate: float = Field(0.50, ge=0.0, le=1.0)
    threshold_high: float = Field(0.75, ge=0.0, le=1.0)


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
