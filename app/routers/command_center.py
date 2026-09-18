from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.command_center_engine import CommandCenterEngine
from app.schemas.command_center import (
    CommandCenterOverviewKPIs,
    IncidentTimelineEvent,
    CommandCenterTrendsResponse,
    CommandCenterSensorHealthResponse
)

router = APIRouter(prefix="/command-center", tags=["Disaster Response Command Center"])

@router.get("/overview", response_model=CommandCenterOverviewKPIs)
def get_command_center_overview(db: Session = Depends(get_db)):
    """
    Returns consolidated high-density control room KPIs, people at risk, active emergencies, and threat levels.
    """
    return CommandCenterEngine.get_overview_kpis(db)

@router.get("/timeline", response_model=List[IncidentTimelineEvent])
def get_incident_timeline(
    limit: int = Query(default=30, ge=1, le=100),
    district: Optional[str] = Query(default=None),
    watershed_id: Optional[int] = Query(default=None),
    risk_level: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Returns real-time chronological disaster incident feed across alerts, sensor breaches, and citizen verified events.
    """
    return CommandCenterEngine.get_incident_timeline(
        db, limit=limit, district=district, watershed_id=watershed_id, risk_level=risk_level
    )

@router.get("/trends", response_model=CommandCenterTrendsResponse)
def get_command_center_trends(
    watershed_id: Optional[int] = Query(default=None),
    time_window: str = Query(default="24h"),
    db: Session = Depends(get_db)
):
    """
    Returns synchronized trend metrics: rainfall, river gauge, soil moisture, predicted levels, and risk score.
    """
    return CommandCenterEngine.get_trends_data(db, watershed_id=watershed_id, time_window=time_window)

@router.get("/sensor-health", response_model=CommandCenterSensorHealthResponse)
def get_sensor_health_audit(db: Session = Depends(get_db)):
    """
    Returns granular telemetry health audit (battery warnings, signal degradation, offline duration).
    """
    return CommandCenterEngine.get_sensor_health_audit(db)
