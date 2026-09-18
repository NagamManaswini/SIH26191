from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.sensor import Sensor
from app.models.enums import SensorType, SensorStatus
from app.schemas.sensor import SensorCreate, SensorUpdate

class CRUDSensor(CRUDBase[Sensor, SensorCreate, SensorUpdate]):
    def get_by_code(self, db: Session, sensor_code: str) -> Optional[Sensor]:
        stmt = select(Sensor).where(Sensor.sensor_code == sensor_code)
        return db.scalars(stmt).first()

    def get_by_type(self, db: Session, sensor_type: SensorType) -> List[Sensor]:
        stmt = select(Sensor).where(Sensor.sensor_type == sensor_type)
        return list(db.scalars(stmt).all())

    def get_active(self, db: Session) -> List[Sensor]:
        stmt = select(Sensor).where(Sensor.status == SensorStatus.ACTIVE)
        return list(db.scalars(stmt).all())

sensor_crud = CRUDSensor(Sensor)
