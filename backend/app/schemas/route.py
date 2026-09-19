"""Pydantic schemas for Safe Evacuation Routing API."""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.common import PointLocation


class RouteCalculationRequest(BaseModel):
    origin: PointLocation = Field(..., json_schema_extra={"example": {"latitude": 19.0600, "longitude": 72.8600}})
    destination: Optional[PointLocation] = Field(None, json_schema_extra={"example": {"latitude": 19.1400, "longitude": 72.9400}})
    destination_shelter_id: Optional[int] = Field(None, json_schema_extra={"example": 1})
    risk_preference: str = Field("strict_safety", json_schema_extra={"example": "strict_safety"})  # strict_safety, balanced, shortest_distance


class RouteCalculationResponse(BaseModel):
    is_safe: bool
    safety_category: str = Field(..., json_schema_extra={"example": "SAFE"})  # SAFE, CAUTION, HIGH_RISK, NO_SAFE_ROUTE
    message: str
    total_distance_km: float = Field(..., ge=0.0, json_schema_extra={"example": 14.5})
    estimated_travel_time_mins: float = Field(..., ge=0.0, json_schema_extra={"example": 21.8})
    estimated_travel_cost: float = Field(..., ge=0.0, json_schema_extra={"example": 14.5})
    route_risk_score: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.05})
    route_geometry: Dict[str, Any]
    waypoints: List[List[float]]

    model_config = ConfigDict(from_attributes=True)
