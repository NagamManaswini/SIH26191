"""
Alerts Router for Real-Time Alert Engine.

Provides endpoints for querying, acknowledging, evaluating, and visualizing
flood early warning alerts, danger zones, and simulated notification broadcasts.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.alert import Alert
from app.models.watershed import Watershed
from app.models.enums import AlertStatus, AlertSeverity, AlertType
from app.schemas.alert import (
    AlertRead,
    AlertCreate,
    AlertUpdate,
    AlertAcknowledgeResponse,
    NotificationLogRead,
    AlertEvaluationResponse,
)
from app.services.alert_engine import alert_engine, calculate_danger_zone_polygon
from app.services.notification_service import notification_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/alerts", tags=["Alerts & Early Warning Engine"])


@router.get("", response_model=List[AlertRead])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get all alerts with optional filtering by status and severity.
    """
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
        
    alerts = query.order_by(desc(Alert.created_at)).offset(offset).limit(limit).all()
    
    results = []
    for a in alerts:
        coords = calculate_danger_zone_polygon(a.latitude, a.longitude, a.radius_km)
        alert_data = AlertRead.model_validate(a)
        alert_data.polygon_coordinates = coords
        results.append(alert_data)
        
    return results


@router.get("/active", response_model=List[AlertRead])
def get_active_alerts(db: Session = Depends(get_db)):
    """
    Get all active alerts currently threatening communities.
    """
    alerts = db.query(Alert).filter(
        Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED])
    ).order_by(desc(Alert.created_at)).all()
    
    results = []
    for a in alerts:
        coords = calculate_danger_zone_polygon(a.latitude, a.longitude, a.radius_km)
        alert_data = AlertRead.model_validate(a)
        alert_data.polygon_coordinates = coords
        results.append(alert_data)
        
    return results


@router.post("/{alert_id}/acknowledge", response_model=AlertAcknowledgeResponse)
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Acknowledge an active emergency alert and broadcast the status update via WebSockets.
    """
    alert = alert_engine.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
        
    coords = calculate_danger_zone_polygon(alert.latitude, alert.longitude, alert.radius_km)
    alert_data = AlertRead.model_validate(alert)
    alert_data.polygon_coordinates = coords
    
    # Broadcast acknowledgment via WebSocket
    await ws_manager.broadcast_json({
        "type": "ALERT_ACKNOWLEDGED",
        "data": {
            "id": alert.id,
            "title": alert.title,
            "status": "ACKNOWLEDGED",
            "acknowledged_at": datetime.now(timezone.utc).isoformat()
        }
    })
    
    return AlertAcknowledgeResponse(
        message="Alert successfully acknowledged.",
        alert=alert_data
    )


@router.post("/evaluate", response_model=AlertEvaluationResponse)
async def trigger_alert_evaluation(
    watershed_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Manually or automatically evaluate hydrological rules and AI predictions to generate/escalate alerts.
    """
    if watershed_id:
        ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not ws:
            raise HTTPException(status_code=404, detail="Watershed not found.")
        eval_results = [alert_engine.evaluate_watershed(db, ws)]
    else:
        eval_results = alert_engine.evaluate_all_watersheds(db)
        
    # If any alert was created/escalated, broadcast via WebSockets
    created_or_escalated = [r for r in eval_results if r.get("action") in ("ALERT_CREATED", "ALERT_ESCALATED")]
    if created_or_escalated:
        await ws_manager.broadcast_json({
            "type": "ALERTS_UPDATED",
            "data": created_or_escalated
        })
        
    return AlertEvaluationResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_evaluated=len(eval_results),
        results=eval_results
    )


@router.get("/zones/geojson")
def get_alert_zones_geojson(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get GeoJSON FeatureCollection of geo-fenced danger polygons around affected alerts.
    """
    active_alerts = db.query(Alert).filter(
        Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED])
    ).all()
    
    features = []
    
    severity_colors = {
        AlertSeverity.EMERGENCY: "#DC2626", # red-600
        AlertSeverity.DANGER: "#EA580C",    # orange-600
        AlertSeverity.WARNING: "#D97706",   # amber-600
        AlertSeverity.INFO: "#2563EB",      # blue-600
        AlertSeverity.ADVISORY: "#2563EB",
        AlertSeverity.WATCH: "#D97706"
    }
    
    for a in active_alerts:
        polygon_coords = calculate_danger_zone_polygon(a.latitude, a.longitude, a.radius_km)
        color = severity_colors.get(a.severity, "#EA580C")
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon_coords]
            },
            "properties": {
                "alert_id": a.id,
                "title": a.title,
                "message": a.message,
                "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
                "alert_type": a.alert_type.value if hasattr(a.alert_type, "value") else str(a.alert_type),
                "center": [a.latitude, a.longitude],
                "radius_km": a.radius_km,
                "status": a.status.value if hasattr(a.status, "value") else str(a.status),
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "expires_at": a.expires_at.isoformat() if a.expires_at else None,
                "color": color,
                "fill_opacity": 0.35 if a.severity in (AlertSeverity.EMERGENCY, AlertSeverity.DANGER) else 0.20
            }
        }
        features.append(feature)
        
    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/notifications/log", response_model=List[NotificationLogRead])
def get_notification_logs(limit: int = Query(default=50, ge=1, le=100)):
    """
    Get recent emergency notification audit logs (SMS, Voice IVR, Mobile Push, Edge Siren).
    """
    logs = notification_service.get_audit_logs(limit=limit)
    return logs
