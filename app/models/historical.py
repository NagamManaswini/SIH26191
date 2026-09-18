from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.enums import RiskLevel

class HistoricalFloodEvent(Base):
    __tablename__ = "historical_flood_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    maximum_rainfall: Mapped[float] = mapped_column(Float, nullable=False)      # mm
    maximum_water_level: Mapped[float] = mapped_column(Float, nullable=False)   # m
    affected_area: Mapped[str] = mapped_column(String(255), nullable=False)     # e.g., "45 sq km across Chamoli"
    severity: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), default=RiskLevel.HIGH, nullable=False, index=True)

    __table_args__ = (
        Index("idx_historical_event_start_sev", "start_time", "severity"),
    )
