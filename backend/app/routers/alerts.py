"""FastAPI Router for Alert Management System (Phase 9)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from backend.app.services.alert_service import (
    get_all_alerts,
    get_alert_by_id,
    create_alert as create_alert_service,
    update_alert as update_alert_service,
)

router = APIRouter(prefix="/alerts", tags=["Alert Management System"])


@router.get("", response_model=List[AlertResponse], summary="List emergency alerts")
def list_alerts(
    severity: Optional[str] = None,
    status_param: Optional[str] = None,
    affected_area: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve emergency alerts filtered by severity (INFO, WARNING, HIGH, CRITICAL) or status."""
    return get_all_alerts(db, severity=severity, status=status_param, affected_area=affected_area)


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED, summary="Create emergency alert")
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    """Create a new emergency alert and dispatch notifications via Web, Email, Push, and SMS providers."""
    return create_alert_service(db, alert_in)


@router.patch("/{id}", response_model=AlertResponse, summary="Update alert status")
def patch_alert(id: int, alert_in: AlertUpdate, db: Session = Depends(get_db)):
    """Update alert status (e.g. ACKNOWLEDGED, RESOLVED, EXPIRED)."""
    updated = update_alert_service(db, alert_id=id, alert_in=alert_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {id} not found.",
        )
    return updated


@router.post("/sos-trigger", summary="Manually trigger emergency SOS alert")
def trigger_sos(
    title: str = "MANUAL EMERGENCY SOS",
    message: str = "Administrator triggered critical emergency alert.",
    affected_area: str = "Chooralmala & Mundakkai Red Zone",
    recommended_action: str = "Immediate evacuation to nearest safe shelter.",
    performed_by: str = "Admin Officer",
    db: Session = Depends(get_db),
):
    """Manually trigger a CRITICAL emergency SOS sound alert."""
    from backend.app.services.alert_service import trigger_manual_sos
    return trigger_manual_sos(
        db=db,
        affected_area=affected_area,
        title=title,
        message=message,
        recommended_action=recommended_action,
        performed_by=performed_by,
    )


@router.post("/sos-stop/{id}", summary="Stop manual SOS alert")
def stop_sos(id: int, performed_by: str = "Admin Officer", db: Session = Depends(get_db)):
    """Deactivate an active emergency SOS alert."""
    from backend.app.services.alert_service import stop_manual_sos
    return stop_manual_sos(db=db, alert_id=id, performed_by=performed_by)


@router.post("/{id}/acknowledge", summary="Acknowledge alert")
def acknowledge_alert(id: int, performed_by: str = "Disaster Official", db: Session = Depends(get_db)):
    """Acknowledge an emergency alert and record audit log."""
    from backend.app.services.alert_service import update_alert_service, log_alert_action
    from backend.app.schemas.alert import AlertUpdate
    updated = update_alert_service(db, alert_id=id, alert_in=AlertUpdate(status="ACKNOWLEDGED"))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Alert {id} not found.")
    log_alert_action(db, alert_id=id, action="ACKNOWLEDGED", performed_by=performed_by, details=f"Alert {id} acknowledged.")
    return {"status": "ACKNOWLEDGED", "alert_id": id}


@router.get("/audit-logs", summary="Get alert audit logs")
def list_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Fetch audit history for alert actions and SOS triggers."""
    from backend.app.services.alert_service import get_audit_logs
    return get_audit_logs(db=db, limit=limit)

