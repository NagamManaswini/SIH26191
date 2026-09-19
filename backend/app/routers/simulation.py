"""FastAPI router for Disaster Simulation Module endpoints."""

from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.simulation import SimulationRequest, SimulationResponse
from backend.app.services.simulation_service import run_deterministic_disaster_simulation

router = APIRouter(prefix="/simulation", tags=["Disaster Simulation Engine"])


@router.post(
    "/run",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute deterministic 9-step disaster simulation",
)
def run_simulation_endpoint(request: SimulationRequest):
    """Execute deterministic 9-step disaster simulation:

    1. Update rainfall conditions
    2. Recalculate hazard scores
    3. Recalculate Red Zones
    4. Identify affected population
    5. Recalculate shelter capacity
    6. Calculate safe evacuation routes
    7. Generate relocation plan
    8. Generate alerts
    9. Update dashboard
    """
    try:
        res = run_deterministic_disaster_simulation(
            rainfall_amount_mm=request.rainfall_amount_mm,
            rainfall_duration_hours=request.rainfall_duration_hours,
            affected_region=request.affected_region,
            population_affected=request.population_affected,
            initial_shelter_occupancy=request.initial_shelter_occupancy,
            slope_deg=request.slope_deg,
            elevation_m=request.elevation_m,
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disaster simulation failed: {str(e)}",
        )
