from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import SensorStatus

class SensorHealthBase(BaseModel):
    sensor_id: int
    battery_level: float
    signal_strength: float
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    status: SensorStatus = SensorStatus.ACTIVE

class SensorHealthCreate(SensorHealthBase):
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


class SensorHealthRead(SensorHealthBase):
    id: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
