from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from app.models.enums import SensorType, SensorStatus

class SensorBase(BaseModel):
    sensor_code: str
    name: str
    sensor_type: SensorType
    latitude: float
    longitude: float
    elevation: float
    village: Optional[str] = None
    watershed_id: Optional[int] = None
    status: SensorStatus = SensorStatus.ACTIVE
    battery_level: float = 100.0

class SensorCreate(SensorBase):
    pass

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    sensor_type: Optional[SensorType] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = None
    village: Optional[str] = None
    watershed_id: Optional[int] = None
    status: Optional[SensorStatus] = None
    battery_level: Optional[float] = None
    last_seen: Optional[datetime] = None

class SensorRead(SensorBase):
    id: int
    last_seen: Optional[datetime] = None
    created_at: datetime
    watershed_name: Optional[str] = None
    latest_reading: Optional[Dict[str, Any]] = None
    signal_strength: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class SensorHealthSnapshot(BaseModel):
    id: int
    sensor_code: str
    name: str
    sensor_type: SensorType
    status: SensorStatus
    battery_level: float
    signal_strength: float
    last_seen: Optional[datetime] = None
    village: Optional[str] = None
    watershed_name: Optional[str] = None

class SensorHealthOverview(BaseModel):
    total_sensors: int
    active_count: int
    offline_count: int
    maintenance_count: int
    inactive_count: int
    avg_battery: float
    low_battery_count: int
    avg_signal: float
    sensors: List[SensorHealthSnapshot]

class TelemetryIngestPayload(BaseModel):
    sensor_code: Optional[str] = None
    sensor_id: Optional[int] = None
    rainfall_mm: Optional[float] = None
    water_level_m: Optional[float] = None
    flow_rate: Optional[float] = None
    moisture_percentage: Optional[float] = None
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None
    status: Optional[SensorStatus] = None
    timestamp: Optional[datetime] = None

class TelemetryIngestResponse(BaseModel):
    status: str
    sensor_id: int
    sensor_code: str
    readings_created: List[str]
    broadcasted: bool
    timestamp: datetime

