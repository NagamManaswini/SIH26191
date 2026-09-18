from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.enums import RiskLevel

class WatershedBase(BaseModel):
    name: str
    code: str
    district: str
    state: str
    area_sq_km: float
    risk_level: RiskLevel = RiskLevel.LOW
    geometry: Optional[str] = None

class WatershedCreate(WatershedBase):
    pass

class WatershedUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    area_sq_km: Optional[float] = None
    risk_level: Optional[RiskLevel] = None
    geometry: Optional[str] = None

class WatershedRead(WatershedBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
