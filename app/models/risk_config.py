from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class RiskConfiguration(Base):
    __tablename__ = "risk_configurations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    config_name: Mapped[str] = mapped_column(String(100), default="Standard Himalayan Monsoon V1", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Weights (Normalized in engine)
    weight_rainfall: Mapped[float] = mapped_column(Float, default=0.25, nullable=False)
    weight_accumulated_rain: Mapped[float] = mapped_column(Float, default=0.15, nullable=False)
    weight_river_level: Mapped[float] = mapped_column(Float, default=0.20, nullable=False)
    weight_rate_of_rise: Mapped[float] = mapped_column(Float, default=0.15, nullable=False)
    weight_soil_moisture: Mapped[float] = mapped_column(Float, default=0.10, nullable=False)
    weight_slope: Mapped[float] = mapped_column(Float, default=0.08, nullable=False)
    weight_historical: Mapped[float] = mapped_column(Float, default=0.07, nullable=False)

    # Critical Dynamic Thresholds
    threshold_rainfall_moderate_mm: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    threshold_rainfall_critical_mm: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    threshold_accumulated_rain_3h_mm: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    threshold_river_danger_m: Mapped[float] = mapped_column(Float, default=3.5, nullable=False)
    threshold_river_critical_m: Mapped[float] = mapped_column(Float, default=4.8, nullable=False)
    threshold_rate_of_rise_m_hr: Mapped[float] = mapped_column(Float, default=0.4, nullable=False)
    threshold_soil_critical_pct: Mapped[float] = mapped_column(Float, default=80.0, nullable=False)
    threshold_slope_steep_deg: Mapped[float] = mapped_column(Float, default=25.0, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
