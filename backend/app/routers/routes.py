from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.route import RouteCalculationRequest, RouteCalculationResponse
from backend.app.services.routing_service import calculate_evacuation_route_service

router = APIRouter(prefix="/routes", tags=["Safe Evacuation Routing"])


@router.post("/calculate", response_model=RouteCalculationResponse, status_code=status.HTTP_200_OK)
def calculate_safe_route(req: RouteCalculationRequest, db: Session = Depends(get_db)):
    """Calculate safe evacuation route using NetworkX & Dijkstra avoiding active Red hazard zones.

    Algorithm Rationale:
    The shortest geographical route is NOT automatically selected if it passes through a high-risk area.
    The algorithm inflates edge weights or bypasses hazard-affected road segments to prioritize citizen safety.
    """
    return calculate_evacuation_route_service(req=req, db=db)
