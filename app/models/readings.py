from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.sensor import Sensor

class RainfallReading(Base):
    __tablename__ = "rainfall_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    rainfall_mm: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="rainfall_readings")

    __table_args__ = (
        Index("idx_rainfall_sensor_timestamp", "sensor_id", "timestamp"),
    )

class RiverReading(Base):
    __tablename__ = "river_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    water_level_m: Mapped[float] = mapped_column(Float, nullable=False)
    flow_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # m^3/s
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="river_readings")

    __table_args__ = (
        Index("idx_river_sensor_timestamp", "sensor_id", "timestamp"),
    )

class SoilMoistureReading(Base):
    __tablename__ = "soil_moisture_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    moisture_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="soil_moisture_readings")

    __table_args__ = (
        Index("idx_soil_moisture_sensor_timestamp", "sensor_id", "timestamp"),
    )
