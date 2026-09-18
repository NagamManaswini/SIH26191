from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Float, String, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import RiskLevel

if TYPE_CHECKING:
    from app.models.watershed import Watershed

class FloodPrediction(Base):
    __tablename__ = "flood_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    watershed_id: Mapped[int] = mapped_column(ForeignKey("watersheds.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    forecast_for: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    predicted_water_level: Mapped[float] = mapped_column(Float, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 100.0%
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)   # 0.0 - 100.0%
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0-temporal", nullable=False)

    # Relationships
    watershed: Mapped["Watershed"] = relationship("Watershed", back_populates="predictions")

    __table_args__ = (
        Index("idx_pred_watershed_forecast", "watershed_id", "forecast_for"),
    )
