"""Pydantic schemas for Relocation Optimization API POST /api/v1/relocation/plan."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PopulationGroupInput(BaseModel):
    id: Optional[int] = None
    location_name: str = Field(..., json_schema_extra={"example": "Red Zone Alpha - Riverside"})
    total_population: int = Field(..., gt=0, json_schema_extra={"example": 150})
    vulnerable_population: int = Field(0, ge=0, json_schema_extra={"example": 45})
    latitude: float = Field(..., ge=-90.0, le=90.0, json_schema_extra={"example": 19.0600})
    longitude: float = Field(..., ge=-180.0, le=180.0, json_schema_extra={"example": 72.8600})


class RelocationPlanRequest(BaseModel):
    population_groups: List[PopulationGroupInput]
    risk_preference: str = Field("strict_safety", json_schema_extra={"example": "strict_safety"})  # strict_safety, balanced, shortest_distance
    max_distance_km: float = Field(50.0, gt=0.0, json_schema_extra={"example": 50.0})


class RelocationAssignmentOutput(BaseModel):
    source_location_name: str
    assigned_population_count: int
    vulnerable_assigned_count: int
    assigned_shelter_id: int
    assigned_shelter_name: str
    distance_km: float
    route_risk_score: float
    shelter_safety_score: float
    shelter_resource_score: float
    suitability_score: float
    route_geometry: Dict[str, Any]
    reason_for_assignment: str

    model_config = ConfigDict(from_attributes=True)


class UnassignedPopulationOutput(BaseModel):
    location_name: str
    unassigned_population: int
    vulnerable_count: int
    reason: str


class RelocationPlanResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "OPTIMAL"})  # OPTIMAL, FEASIBLE_PARTIAL, INFEASIBLE_FULL_CAPACITY
    message: str
    assignments: List[RelocationAssignmentOutput]
    unassigned_populations: List[UnassignedPopulationOutput]
    total_evacuated: int
    total_unassigned: int
    optimization_summary: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
