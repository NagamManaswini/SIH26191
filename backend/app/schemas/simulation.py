"""Pydantic request/response schemas for Disaster Simulation Module."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    rainfall_amount_mm: float = Field(200.0, description="Simulated rainfall amount in mm", ge=0.0)
    rainfall_duration_hours: float = Field(6.0, description="Simulated rainfall duration in hours", gt=0.0)
    affected_region: str = Field("Riverside & Foothill Region", description="Name of affected geographic region")
    population_affected: int = Field(550, description="Number of citizens in affected region", ge=0)
    initial_shelter_occupancy: int = Field(600, description="Initial total occupancy across shelters", ge=0)
    slope_deg: float = Field(38.0, description="Average terrain slope angle in degrees", ge=0.0, le=90.0)
    elevation_m: float = Field(650.0, description="Average elevation in meters above sea level", ge=0.0)


class SimulationStepResult(BaseModel):
    step_number: int
    step_name: str
    status: str = "COMPLETED"
    summary: str
    details: Dict[str, Any]


class SimulationResponse(BaseModel):
    simulation_id: str
    timestamp: str
    deterministic_seed: int = 20260826
    parameters: Dict[str, Any]
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    workflow_steps: List[SimulationStepResult]
    alerts: List[Dict[str, Any]]
