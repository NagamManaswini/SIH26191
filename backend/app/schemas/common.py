"""Common schema types and base Pydantic models."""

from typing import List, Tuple, Optional, Any, Dict
from pydantic import BaseModel, Field


class PointLocation(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude degree")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude degree")


class PolygonCoordinates(BaseModel):
    # Outer ring coordinates: [[lon, lat], [lon, lat], ...]
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="GeoJSON style polygon coordinates array: [[[lon, lat], ...]]"
    )


class HealthResponse(BaseModel):
    status: str = "healthy"
    database_status: str
    app_name: str
    version: str = "1.0.0"
    timestamp: str
