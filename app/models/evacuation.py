from typing import Optional
from sqlalchemy import String, Float, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class EvacuationCenter(Base):
    __tablename__ = "evacuation_centers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    current_occupancy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(100), default="Rudraprayag", nullable=True)
    elevation_m: Mapped[Optional[float]] = mapped_column(Float, default=2100.0, nullable=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    facilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # e.g., JSON list or description of amenities

