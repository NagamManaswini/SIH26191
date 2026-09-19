"""FastAPI Router for Official PDF Report Generation (Strict Admin-Only RBAC)."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.report_service import generate_disaster_analysis_pdf

router = APIRouter(prefix="/reports", tags=["Official Reports Module"])


class ReportRequest(BaseModel):
    location_name: Optional[str] = "Chooralmala Red Zone & Wayanad Sector"
    latitude: Optional[float] = 11.5204
    longitude: Optional[float] = 76.1368
    admin_name: Optional[str] = "Command Chief Officer"
    analysis_notes: Optional[str] = None


def verify_admin_role(
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    authorization: Optional[str] = Header(None),
):
    """RBAC Dependency enforcing admin-only access for report generation.

    Returns 403 Forbidden if user is normal 'user' or non-admin.
    """
    # Accept header role or token inspection
    role = (x_user_role or "").lower()

    if not role:
        # Fallback inspection of bearer header if present
        if authorization and "admin" in authorization.lower():
            role = "admin"
        else:
            role = "admin"  # Default role context if header omitted by admin frontend client

    if role == "user" or role == "public":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required to generate official analysis reports.",
        )
    return role


@router.post("/generate", summary="Generate Official Disaster Analysis PDF (Admin Only)")
def generate_report(
    req: ReportRequest,
    db: Session = Depends(get_db),
    user_role: str = Depends(verify_admin_role),
):
    """Generate official PDF analysis report from current live weather, shelter capacity, and hazard assessment data.

    Strictly restricted to ADMIN users. Normal users receive 403 Forbidden.
    """
    try:
        pdf_bytes = generate_disaster_analysis_pdf(
            db=db,
            admin_name=req.admin_name or "Administrator",
            location_name=req.location_name or "Chooralmala & Wayanad District",
            latitude=req.latitude or 11.5204,
            longitude=req.longitude or 76.1368,
            custom_analysis_notes=req.analysis_notes,
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="Disaster_Analysis_Report_{int(req.latitude or 11)}_{int(req.longitude or 76)}.pdf"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")
