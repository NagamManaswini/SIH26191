from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.enums import AlertType, AlertSeverity, AlertStatus

class AlertBase(BaseModel):
    alert_type: AlertType = AlertType.FLASH_FLOOD
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str
    message: str
    latitude: float
    longitude: float
    radius_km: float = 5.0
    expires_at: Optional[datetime] = None
    status: AlertStatus = AlertStatus.ACTIVE

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    expires_at: Optional[datetime] = None
    status: Optional[AlertStatus] = None

class AlertRead(AlertBase):
    id: int
    created_at: datetime
    polygon_coordinates: Optional[List[List[float]]] = None

    model_config = ConfigDict(from_attributes=True)

class AlertAcknowledgeResponse(BaseModel):
    message: str
    alert: AlertRead

class NotificationLogRead(BaseModel):
    dispatch_id: str
    provider: str
    channel: str
    recipient: str
    severity: str
    title: str
    message: str
    status: str
    timestamp: str
    latency_ms: Optional[int] = None
    tone_pattern: Optional[str] = None
    script_spoken: Optional[str] = None
    active_devices_reached: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class AlertEvaluationResultItem(BaseModel):
    watershed_id: int
    watershed_name: str
    action: str
    alert_id: Optional[int] = None
    severity: Optional[str] = None
    reasons: Optional[List[str]] = None
    dispatches: Optional[int] = None
    existing_alert_id: Optional[int] = None

class AlertEvaluationResponse(BaseModel):
    timestamp: str
    total_evaluated: int
    results: List[AlertEvaluationResultItem]
