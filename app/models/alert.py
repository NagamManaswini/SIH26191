from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Text, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.enums import AlertType, AlertSeverity, AlertStatus

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    alert_type: Mapped[AlertType] = mapped_column(SQLEnum(AlertType), default=AlertType.FLASH_FLOOD, nullable=False, index=True)
    severity: Mapped[AlertSeverity] = mapped_column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_km: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    status: Mapped[AlertStatus] = mapped_column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False, index=True)

    __table_args__ = (
        Index("idx_alert_status_created", "status", "created_at"),
    )
