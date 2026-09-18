from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class EvacuationCenterBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    capacity: int
    current_occupancy: int = 0
    is_active: bool = True
    district: Optional[str] = "Rudraprayag"
    elevation_m: Optional[float] = 2100.0
    contact_number: Optional[str] = None
    facilities: Optional[str] = None

class EvacuationCenterCreate(EvacuationCenterBase):
    pass

class EvacuationCenterUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    is_active: Optional[bool] = None
    district: Optional[str] = None
    elevation_m: Optional[float] = None
    contact_number: Optional[str] = None
    facilities: Optional[str] = None

class EvacuationCenterRead(EvacuationCenterBase):
    id: int
    available_capacity: int = 0
    occupancy_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class NearestCenterItem(EvacuationCenterRead):
    distance_km: float
    safety_score: float = 95.0

class EvacuationRouteStep(BaseModel):
    step_number: int
    instruction: str
    distance_km: float
    elevation_change_m: str
    hazard_status: str

class ElevationProfilePoint(BaseModel):
    distance_km: float
    elevation_m: float
    latitude: float
    longitude: float

class EvacuationRouteResponse(BaseModel):
    origin: Dict[str, float]
    destination: Dict[str, Any]
    total_distance_km: float
    estimated_walking_time_min: int
    estimated_driving_time_min: int
    safety_index_pct: float
    waypoints: List[List[float]]
    elevation_profile: List[ElevationProfilePoint]
    turn_by_turn_steps: List[EvacuationRouteStep]
    hazard_avoidance_logs: List[str]
