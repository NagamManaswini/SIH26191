from typing import List
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.schemas.readings import (
    RainfallReadingCreate,
    RiverReadingCreate,
    SoilMoistureReadingCreate,
)

class CRUDRainfall(CRUDBase[RainfallReading, RainfallReadingCreate, RainfallReadingCreate]):
    def get_latest_by_sensor(self, db: Session, sensor_id: int, limit: int = 50) -> List[RainfallReading]:
        stmt = (
            select(RainfallReading)
            .where(RainfallReading.sensor_id == sensor_id)
            .order_by(desc(RainfallReading.timestamp))
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

class CRUDRiver(CRUDBase[RiverReading, RiverReadingCreate, RiverReadingCreate]):
    def get_latest_by_sensor(self, db: Session, sensor_id: int, limit: int = 50) -> List[RiverReading]:
        stmt = (
            select(RiverReading)
            .where(RiverReading.sensor_id == sensor_id)
            .order_by(desc(RiverReading.timestamp))
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

class CRUDSoilMoisture(CRUDBase[SoilMoistureReading, SoilMoistureReadingCreate, SoilMoistureReadingCreate]):
    def get_latest_by_sensor(self, db: Session, sensor_id: int, limit: int = 50) -> List[SoilMoistureReading]:
        stmt = (
            select(SoilMoistureReading)
            .where(SoilMoistureReading.sensor_id == sensor_id)
            .order_by(desc(SoilMoistureReading.timestamp))
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

rainfall_crud = CRUDRainfall(RainfallReading)
river_crud = CRUDRiver(RiverReading)
soil_moisture_crud = CRUDSoilMoisture(SoilMoistureReading)
