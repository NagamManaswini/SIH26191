from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import SensorType, SensorStatus

if TYPE_CHECKING:
    from app.models.watershed import Watershed
    from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
    from app.models.sensor_health import SensorHealth

class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    sensor_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sensor_type: Mapped[SensorType] = mapped_column(SQLEnum(SensorType), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    elevation: Mapped[float] = mapped_column(Float, nullable=False)
    village: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    watershed_id: Mapped[Optional[int]] = mapped_column(ForeignKey("watersheds.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[SensorStatus] = mapped_column(SQLEnum(SensorStatus), default=SensorStatus.ACTIVE, nullable=False, index=True)
    battery_level: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    watershed: Mapped[Optional["Watershed"]] = relationship("Watershed", back_populates="sensors")
    rainfall_readings: Mapped[List["RainfallReading"]] = relationship("RainfallReading", back_populates="sensor", cascade="all, delete-orphan")
    river_readings: Mapped[List["RiverReading"]] = relationship("RiverReading", back_populates="sensor", cascade="all, delete-orphan")
    soil_moisture_readings: Mapped[List["SoilMoistureReading"]] = relationship("SoilMoistureReading", back_populates="sensor", cascade="all, delete-orphan")
    health_logs: Mapped[List["SensorHealth"]] = relationship("SensorHealth", back_populates="sensor", cascade="all, delete-orphan")
