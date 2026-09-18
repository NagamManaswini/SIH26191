from app.schemas.user import UserBase, UserCreate, UserUpdate, UserRead
from app.schemas.watershed import WatershedBase, WatershedCreate, WatershedUpdate, WatershedRead
from app.schemas.sensor import SensorBase, SensorCreate, SensorUpdate, SensorRead
from app.schemas.readings import (
    RainfallReadingBase, RainfallReadingCreate, RainfallReadingRead,
    RiverReadingBase, RiverReadingCreate, RiverReadingRead,
    SoilMoistureReadingBase, SoilMoistureReadingCreate, SoilMoistureReadingRead
)
from app.schemas.prediction import FloodPredictionBase, FloodPredictionCreate, FloodPredictionRead
from app.schemas.alert import AlertBase, AlertCreate, AlertUpdate, AlertRead
from app.schemas.citizen_report import CitizenReportBase, CitizenReportCreate, CitizenReportUpdate, CitizenReportRead
from app.schemas.evacuation import EvacuationCenterBase, EvacuationCenterCreate, EvacuationCenterUpdate, EvacuationCenterRead
from app.schemas.historical import HistoricalFloodEventBase, HistoricalFloodEventCreate, HistoricalFloodEventRead
from app.schemas.sensor_health import SensorHealthBase, SensorHealthCreate, SensorHealthRead

__all__ = [
    "UserBase", "UserCreate", "UserUpdate", "UserRead",
    "WatershedBase", "WatershedCreate", "WatershedUpdate", "WatershedRead",
    "SensorBase", "SensorCreate", "SensorUpdate", "SensorRead",
    "RainfallReadingBase", "RainfallReadingCreate", "RainfallReadingRead",
    "RiverReadingBase", "RiverReadingCreate", "RiverReadingRead",
    "SoilMoistureReadingBase", "SoilMoistureReadingCreate", "SoilMoistureReadingRead",
    "FloodPredictionBase", "FloodPredictionCreate", "FloodPredictionRead",
    "AlertBase", "AlertCreate", "AlertUpdate", "AlertRead",
    "CitizenReportBase", "CitizenReportCreate", "CitizenReportUpdate", "CitizenReportRead",
    "EvacuationCenterBase", "EvacuationCenterCreate", "EvacuationCenterUpdate", "EvacuationCenterRead",
    "HistoricalFloodEventBase", "HistoricalFloodEventCreate", "HistoricalFloodEventRead",
    "SensorHealthBase", "SensorHealthCreate", "SensorHealthRead",
]
