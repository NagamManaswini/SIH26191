from backend.app.schemas.common import HealthResponse, PointLocation, PolygonCoordinates
from backend.app.schemas.shelter import (
    ShelterCreate,
    ShelterUpdate,
    ShelterResponse,
    ShelterCapacityMetricsResponse,
    ShelterEvaluateRequest,
    ShelterEvaluateResponse,
)
from backend.app.schemas.hazard_zone import HazardZoneCreate, HazardZoneUpdate, HazardZoneResponse, HazardAnalyzeRequest
from backend.app.schemas.population import PopulationCreate, PopulationUpdate, PopulationResponse
from backend.app.schemas.rainfall import RainfallRecordCreate, RainfallRecordUpdate, RainfallRecordResponse
from backend.app.schemas.risk import RiskPredictionRequest, RiskPredictionResponse
from backend.app.schemas.route import RouteCalculationRequest, RouteCalculationResponse
from backend.app.schemas.relocation import (
    PopulationGroupInput,
    RelocationPlanRequest,
    RelocationAssignmentOutput,
    UnassignedPopulationOutput,
    RelocationPlanResponse,
)

__all__ = [
    "HealthResponse",
    "PointLocation",
    "PolygonCoordinates",
    "ShelterCreate",
    "ShelterUpdate",
    "ShelterResponse",
    "ShelterCapacityMetricsResponse",
    "ShelterEvaluateRequest",
    "ShelterEvaluateResponse",
    "HazardZoneCreate",
    "HazardZoneUpdate",
    "HazardZoneResponse",
    "HazardAnalyzeRequest",
    "PopulationCreate",
    "PopulationUpdate",
    "PopulationResponse",
    "RainfallRecordCreate",
    "RainfallRecordUpdate",
    "RainfallRecordResponse",
    "RiskPredictionRequest",
    "RiskPredictionResponse",
    "RouteCalculationRequest",
    "RouteCalculationResponse",
    "PopulationGroupInput",
    "RelocationPlanRequest",
    "RelocationAssignmentOutput",
    "UnassignedPopulationOutput",
    "RelocationPlanResponse",
]
