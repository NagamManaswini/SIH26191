from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import RiskLevel

class FloodPredictionBase(BaseModel):
    watershed_id: int
    forecast_for: datetime
    predicted_water_level: float
    probability: float
    risk_level: RiskLevel = RiskLevel.LOW
    confidence: float
    model_version: str = "v1.0-temporal"

class FloodPredictionCreate(FloodPredictionBase):
    prediction_time: datetime = Field(default_factory=datetime.utcnow)


class FloodPredictionRead(FloodPredictionBase):
    id: int
    prediction_time: datetime

    model_config = ConfigDict(from_attributes=True)
