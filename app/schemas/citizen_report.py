from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.enums import CitizenReportType, VerificationStatus

class NearbySensorMatchItem(BaseModel):
    sensor_id: int
    sensor_name: str
    sensor_type: str
    latitude: float
    longitude: float
    distance_km: float
    status: str
    latest_reading: Optional[Dict[str, Any]] = None
    is_corroborating: bool = False
    corroboration_note: Optional[str] = None

class CitizenReportBase(BaseModel):
    user_id: Optional[int] = None
    report_type: CitizenReportType = CitizenReportType.RIVER_RISING
    description: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING

class CitizenReportCreate(BaseModel):
    report_type: CitizenReportType = CitizenReportType.RIVER_RISING
    description: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    user_id: Optional[int] = None

class CitizenReportVerifyPayload(BaseModel):
    verification_status: VerificationStatus
    verification_notes: Optional[str] = None

class CitizenReportUpdate(BaseModel):
    verification_status: Optional[VerificationStatus] = None
    verification_notes: Optional[str] = None
    description: Optional[str] = None

class CitizenReportRead(CitizenReportBase):
    id: int
    confidence_score: Optional[float] = 50.0
    verified_by_user_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CitizenReportDetail(CitizenReportRead):
    nearby_sensors_count: int = 0
    corroborating_sensors_count: int = 0
    nearby_sensors: List[NearbySensorMatchItem] = []
    matching_reasons: List[str] = []
