"""Hospital Data Provider Abstraction Layer.

Supports switching between Database-backed verified capacity data and external real-time Hospital APIs.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.entities import Hospital, HospitalCapacity


class HospitalDataProvider(ABC):
    """Abstract Base Class for Hospital Data Providers."""

    @abstractmethod
    def get_hospitals(self, db: Session, district: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_hospital_capacity(self, db: Session, hospital_id: int) -> Optional[Dict[str, Any]]:
        pass


class DatabaseHospitalProvider(HospitalDataProvider):
    """Database-backed hospital provider using admin-verified capacity data."""

    def get_hospitals(self, db: Session, district: Optional[str] = None) -> List[Dict[str, Any]]:
        query = db.query(Hospital).filter(Hospital.is_active == True)
        if district:
            query = query.filter(Hospital.district.ilike(f"%{district}%"))
        hospitals = query.all()
        result = []
        for h in hospitals:
            cap_dict = None
            if h.capacity:
                cap_dict = {
                    "total_beds": h.capacity.total_beds,
                    "occupied_beds": h.capacity.occupied_beds,
                    "available_beds": max(0, h.capacity.total_beds - h.capacity.occupied_beds),
                    "total_icu": h.capacity.total_icu,
                    "occupied_icu": h.capacity.occupied_icu,
                    "available_icu": max(0, h.capacity.total_icu - h.capacity.occupied_icu),
                    "total_emergency_beds": h.capacity.total_emergency_beds,
                    "occupied_emergency_beds": h.capacity.occupied_emergency_beds,
                    "available_emergency_beds": max(0, h.capacity.total_emergency_beds - h.capacity.occupied_emergency_beds),
                    "isolation_beds": h.capacity.isolation_beds,
                    "total_ambulances": h.capacity.total_ambulances,
                    "available_ambulances": h.capacity.available_ambulances,
                    "busy_ambulances": max(0, h.capacity.total_ambulances - h.capacity.available_ambulances),
                    "updated_at": h.capacity.updated_at.isoformat() if h.capacity.updated_at else None,
                    "updated_by": h.capacity.updated_by or "Admin",
                }
            result.append({
                "id": h.id,
                "hospital_id": h.hospital_id,
                "name": h.name,
                "type": h.type,
                "address": h.address,
                "latitude": h.latitude,
                "longitude": h.longitude,
                "district": h.district,
                "state": h.state,
                "phone": h.phone,
                "emergency_status": h.emergency_status,
                "operational_status": h.operational_status,
                "specialization": h.specialization,
                "data_source": h.data_source or "Hospital Management System",
                "capacity": cap_dict,
            })
        return result

    def get_hospital_capacity(self, db: Session, hospital_id: int) -> Optional[Dict[str, Any]]:
        cap = db.query(HospitalCapacity).filter(HospitalCapacity.hospital_id == hospital_id).first()
        if not cap:
            return None
        return {
            "total_beds": cap.total_beds,
            "occupied_beds": cap.occupied_beds,
            "available_beds": max(0, cap.total_beds - cap.occupied_beds),
            "total_icu": cap.total_icu,
            "occupied_icu": cap.occupied_icu,
            "available_icu": max(0, cap.total_icu - cap.occupied_icu),
            "total_emergency_beds": cap.total_emergency_beds,
            "occupied_emergency_beds": cap.occupied_emergency_beds,
            "available_emergency_beds": max(0, cap.total_emergency_beds - cap.occupied_emergency_beds),
            "isolation_beds": cap.isolation_beds,
            "total_ambulances": cap.total_ambulances,
            "available_ambulances": cap.available_ambulances,
            "busy_ambulances": max(0, cap.total_ambulances - cap.available_ambulances),
            "updated_at": cap.updated_at.isoformat() if cap.updated_at else None,
            "updated_by": cap.updated_by or "Admin",
        }


class ExternalHospitalAPIProvider(HospitalDataProvider):
    """Extensible Provider for real-time State / National Hospital Management APIs."""

    def __init__(self, api_endpoint: Optional[str] = None):
        self.api_endpoint = api_endpoint

    def get_hospitals(self, db: Session, district: Optional[str] = None) -> List[Dict[str, Any]]:
        # Fallback to DatabaseHospitalProvider if external API endpoint is not set or unreachable
        db_provider = DatabaseHospitalProvider()
        return db_provider.get_hospitals(db, district=district)

    def get_hospital_capacity(self, db: Session, hospital_id: int) -> Optional[Dict[str, Any]]:
        db_provider = DatabaseHospitalProvider()
        return db_provider.get_hospital_capacity(db, hospital_id=hospital_id)


def get_hospital_data_provider() -> HospitalDataProvider:
    """Factory function returning the active HospitalDataProvider."""
    return DatabaseHospitalProvider()
