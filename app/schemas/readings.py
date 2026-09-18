from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Rainfall Reading
class RainfallReadingBase(BaseModel):
    sensor_id: int
    rainfall_mm: float
    timestamp: Optional[datetime] = None

class RainfallReadingCreate(RainfallReadingBase):
    pass

class RainfallReadingRead(BaseModel):
    id: int
    sensor_id: int
    rainfall_mm: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# River Reading
class RiverReadingBase(BaseModel):
    sensor_id: int
    water_level_m: float
    flow_rate: Optional[float] = None
    timestamp: Optional[datetime] = None

class RiverReadingCreate(RiverReadingBase):
    pass

class RiverReadingRead(BaseModel):
    id: int
    sensor_id: int
    water_level_m: float
    flow_rate: Optional[float] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Soil Moisture Reading
class SoilMoistureReadingBase(BaseModel):
    sensor_id: int
    moisture_percentage: float
    timestamp: Optional[datetime] = None

class SoilMoistureReadingCreate(SoilMoistureReadingBase):
    pass

class SoilMoistureReadingRead(BaseModel):
    id: int
    sensor_id: int
    moisture_percentage: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
