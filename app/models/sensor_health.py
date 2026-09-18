from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Float, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import SensorStatus

if TYPE_CHECKING:
    from app.models.sensor import Sensor

class SensorHealth(Base):
    __tablename__ = "sensor_health_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    battery_level: Mapped[float] = mapped_column(Float, nullable=False)
    signal_strength: Mapped[float] = mapped_column(Float, nullable=False)  # RSSI in dBm or percentage
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[SensorStatus] = mapped_column(SQLEnum(SensorStatus), default=SensorStatus.ACTIVE, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="health_logs")

    __table_args__ = (
        Index("idx_sensor_health_sensor_recorded", "sensor_id", "recorded_at"),
    )
