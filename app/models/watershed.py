from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import RiskLevel

if TYPE_CHECKING:
    from app.models.sensor import Sensor
    from app.models.prediction import FloodPrediction

class Watershed(Base):
    __tablename__ = "watersheds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    area_sq_km: Mapped[float] = mapped_column(Float, nullable=False)
    average_slope_deg: Mapped[float] = mapped_column(Float, default=24.5, nullable=False)
    elevation_m: Mapped[float] = mapped_column(Float, default=1850.0, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)
    geometry: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # GeoJSON string polygon

    # Relationships
    sensors: Mapped[List["Sensor"]] = relationship("Sensor", back_populates="watershed")
    predictions: Mapped[List["FloodPrediction"]] = relationship("FloodPrediction", back_populates="watershed", cascade="all, delete-orphan")
