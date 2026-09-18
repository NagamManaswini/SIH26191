from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, Text, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import CitizenReportType, VerificationStatus

if TYPE_CHECKING:
    from app.models.user import User

class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    report_type: Mapped[CitizenReportType] = mapped_column(SQLEnum(CitizenReportType), default=CitizenReportType.WATER_OVERFLOW, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Text allows base64 or long image URLs
    verification_status: Mapped[VerificationStatus] = mapped_column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False, index=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, default=50.0, nullable=True)
    verified_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="citizen_reports", foreign_keys=[user_id])
    verified_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by_user_id])

    __table_args__ = (
        Index("idx_citizen_report_status_created", "verification_status", "created_at"),
    )
