from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class CommandCenterOverviewKPIs(BaseModel):
    active_emergencies: int
    critical_watersheds: int
    high_risk_zones: int
    active_alerts: int
    online_sensors: int
    offline_sensors: int
    citizen_reports: int
    people_at_risk: int
    threat_level: str  # "DEFCON 1 (CRITICAL)", "DEFCON 2 (SEVERE)", "DEFCON 3 (ELEVATED)", "DEFCON 4 (NORMAL)"
    system_readiness_pct: float
    last_updated: str

class IncidentTimelineEvent(BaseModel):
    id: str
    event_type: str  # "ALERT_ISSUED", "SENSOR_BREACH", "CITIZEN_REPORT", "SHELTER_UPDATE"
    severity: str    # "CRITICAL", "HIGH", "MODERATE", "LOW", "INFO"
    title: str
    description: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: str
    source: str
    status: str

class TimeSeriesPoint(BaseModel):
    timestamp: str
    rainfall_mm: float
    river_level_m: float
    soil_moisture_pct: float
    predicted_level_m: Optional[float] = None
    risk_score: float

class CommandCenterTrendsResponse(BaseModel):
    watershed_id: Optional[int] = None
    watershed_name: Optional[str] = None
    time_window: str
    series: List[TimeSeriesPoint]

class SensorHealthAuditItem(BaseModel):
    id: int
    sensor_code: str
    name: str
    sensor_type: str
    status: str
    battery_level: float
    signal_strength: float
    last_communication: Optional[str] = None
    has_battery_warning: bool
    has_signal_warning: bool
    offline_duration_hours: float = 0.0

class CommandCenterSensorHealthResponse(BaseModel):
    total_sensors: int
    online_count: int
    offline_count: int
    battery_warnings_count: int
    signal_warnings_count: int
    sensors: List[SensorHealthAuditItem]
