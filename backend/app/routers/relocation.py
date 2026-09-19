from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.relocation import RelocationPlanRequest, RelocationPlanResponse
from backend.app.services.relocation_service import generate_relocation_plan_service

router = APIRouter(prefix="/relocation", tags=["Intelligent Relocation Engine"])


@router.post("/plan", response_model=RelocationPlanResponse, status_code=status.HTTP_200_OK)
def plan_relocation(req: RelocationPlanRequest, db: Session = Depends(get_db)):
    """Generate optimal evacuation relocation plan assigning vulnerable populations to safe shelters.

    Optimization Objectives:
    1. Do not exceed shelter carrying capacity limits.
    2. Prefer safer, well-resourced shelters.
    3. Minimize unnecessary travel distance.
    4. Avoid dangerous hazard routes.
    5. Prioritize vulnerable populations (elderly, children, medical priority).
    """
    return generate_relocation_plan_service(req=req, db=db)
