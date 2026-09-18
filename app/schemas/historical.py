from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import RiskLevel

class HistoricalFloodEventBase(BaseModel):
    name: str
    location: str
    start_time: datetime
    end_time: Optional[datetime] = None
    maximum_rainfall: float
    maximum_water_level: float
    affected_area: str
    severity: RiskLevel = RiskLevel.HIGH

class HistoricalFloodEventCreate(HistoricalFloodEventBase):
    pass

class HistoricalFloodEventRead(HistoricalFloodEventBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
