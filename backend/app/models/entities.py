"""SQLAlchemy database models for SIH26191 Disaster Management Platform."""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship

from backend.app.database import Base
from backend.app.models.base_spatial import SpatialPoint, SpatialPolygon, SpatialLineString


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="public", index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    district = Column(String(255), index=True, nullable=True)
    state = Column(String(255), index=True, nullable=True)
    coordinates = Column(SpatialPoint, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    population_records = relationship("Population", back_populates="location")


class Population(Base):
    __tablename__ = "population"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(255), index=True, nullable=False)
    total_population = Column(Integer, nullable=False)
    vulnerable_population = Column(Integer, default=0)
    density_per_sq_km = Column(Float, default=0.0)
    area_geometry = Column(SpatialPolygon, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    location = relationship("Location", back_populates="population_records")


class Shelter(Base):
    __tablename__ = "shelters"
    __table_args__ = (
        CheckConstraint("current_occupancy <= capacity", name="check_shelter_capacity_limit"),
        CheckConstraint("current_occupancy >= 0", name="check_shelter_occupancy_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    address = Column(String(500), nullable=True)
    capacity = Column(Integer, nullable=False)
    current_occupancy = Column(Integer, default=0)
    status = Column(String(50), default="active", index=True)
    contact_number = Column(String(50), nullable=True)
    accessibility_rating = Column(Float, default=0.8)
    structural_safety_rating = Column(Float, default=0.9)
    location = Column(SpatialPoint, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    resources = relationship("ShelterResource", back_populates="shelter", uselist=False, cascade="all, delete-orphan")
    evacuation_routes = relationship("EvacuationRoute", back_populates="destination_shelter")
    relocation_assignments = relationship("RelocationAssignment", back_populates="shelter")


class ShelterResource(Base):
    __tablename__ = "shelter_resources"

    id = Column(Integer, primary_key=True, index=True)
    shelter_id = Column(Integer, ForeignKey("shelters.id", ondelete="CASCADE"), nullable=False, unique=True)
    water_supply_days = Column(Float, default=0.0)
    food_supply_days = Column(Float, default=0.0)
    medical_kits = Column(Integer, default=0)
    power_backup = Column(Boolean, default=False)
    sanitation_facilities = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    shelter = relationship("Shelter", back_populates="resources")


class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    road_type = Column(String(100), default="primary")
    condition = Column(String(100), default="good")
    passable = Column(Boolean, default=True, index=True)
    path = Column(SpatialLineString, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HazardZone(Base):
    __tablename__ = "hazard_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    hazard_type = Column(String(100), nullable=False, index=True)
    risk_level = Column(String(50), nullable=False, index=True)  # RED, YELLOW, GREEN, CRITICAL
    risk_score = Column(Float, default=0.0)
    boundary = Column(SpatialPolygon, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RainfallRecord(Base):
    __tablename__ = "rainfall_records"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(255), index=True, nullable=False)
    rainfall_mm = Column(Float, nullable=False)
    duration_hours = Column(Float, default=24.0)
    intensity = Column(String(50), default="moderate")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    station_location = Column(SpatialPoint, nullable=True)


class DisasterEvent(Base):
    __tablename__ = "disaster_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    event_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), default="active", index=True)
    affected_area = Column(SpatialPolygon, nullable=True)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    relocation_assignments = relationship("RelocationAssignment", back_populates="disaster_event")


class EvacuationRoute(Base):
    __tablename__ = "evacuation_routes"

    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String(255), nullable=False)
    origin_location = Column(SpatialPoint, nullable=False)
    destination_shelter_id = Column(Integer, ForeignKey("shelters.id"), nullable=True)
    route_path = Column(SpatialLineString, nullable=False)
    distance_km = Column(Float, default=0.0)
    estimated_travel_time_mins = Column(Float, default=0.0)
    is_safe = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    destination_shelter = relationship("Shelter", back_populates="evacuation_routes")


class RelocationAssignment(Base):
    __tablename__ = "relocation_assignments"

    id = Column(Integer, primary_key=True, index=True)
    disaster_event_id = Column(Integer, ForeignKey("disaster_events.id"), nullable=True)
    source_location_name = Column(String(255), nullable=False)
    shelter_id = Column(Integer, ForeignKey("shelters.id"), nullable=False)
    assigned_population_count = Column(Integer, nullable=False)
    status = Column(String(50), default="assigned", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    disaster_event = relationship("DisasterEvent", back_populates="relocation_assignments")
    shelter = relationship("Shelter", back_populates="relocation_assignments")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False, default="INFO", index=True)
    affected_area = Column(String(255), nullable=False, default="General District")
    recommended_action = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)
    created_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("severity IN ('INFO', 'WARNING', 'HIGH', 'CRITICAL')", name="check_alert_severity"),
        CheckConstraint("status IN ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'EXPIRED')", name="check_alert_status"),
    )


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(String(100), unique=True, index=True, nullable=False)
    owner_id = Column(String(100), nullable=True, index=True)
    owner_name = Column(String(255), nullable=True)
    animal_type = Column(String(100), nullable=False, index=True)  # cattle, goats, sheep, dogs, cats, poultry, other_livestock
    name = Column(String(255), nullable=True)
    location_name = Column(String(255), nullable=False, default="Red Zone Alpha")
    coordinates = Column(SpatialPoint, nullable=True)
    emergency_status = Column(String(50), default="AT_RISK", index=True)  # SAFE, AT_RISK, EVACUATING, RELOCATED
    rescue_status = Column(String(50), default="PENDING", index=True)  # PENDING, IN_PROGRESS, COMPLETED, UNASSIGNED
    destination_shelter_id = Column(Integer, ForeignKey("animal_shelters.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    destination_shelter = relationship("AnimalShelter", back_populates="assigned_animals")


class AnimalShelter(Base):
    __tablename__ = "animal_shelters"
    __table_args__ = (
        CheckConstraint("current_occupancy <= capacity", name="check_animal_shelter_capacity"),
        CheckConstraint("current_occupancy >= 0", name="check_animal_shelter_occupancy_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    address = Column(String(500), nullable=True)
    capacity = Column(Integer, nullable=False, default=200)
    current_occupancy = Column(Integer, default=0)
    supported_animal_types = Column(String(500), default="cattle,goats,sheep,dogs,cats,poultry,other_livestock")
    water_availability = Column(Boolean, default=True)
    food_availability = Column(Boolean, default=True)
    safety_status = Column(String(50), default="SAFE", index=True)
    location = Column(SpatialPoint, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assigned_animals = relationship("Animal", back_populates="destination_shelter")
    rescue_assignments = relationship("AnimalRescueAssignment", back_populates="animal_shelter")


class AnimalRescueAssignment(Base):
    __tablename__ = "animal_rescue_assignments"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    animal_shelter_id = Column(Integer, ForeignKey("animal_shelters.id"), nullable=False)
    assigned_by = Column(String(100), default="System Optimizer")
    status = Column(String(50), default="ASSIGNED", index=True)  # ASSIGNED, EN_ROUTE, COMPLETED, CANCELLED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    animal_shelter = relationship("AnimalShelter", back_populates="rescue_assignments")


class CommunicationMessage(Base):
    __tablename__ = "communication_messages"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, default="GENERAL", index=True)  # GENERAL, EVACUATION, ANIMAL_SAFETY, SHELTER, ROAD_BLOCK, WEATHER, EMERGENCY
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    target_area = Column(String(255), nullable=False, default="ALL")
    severity = Column(String(50), nullable=False, default="INFO", index=True)  # INFO, WARNING, HIGH, CRITICAL
    sender_name = Column(String(255), nullable=False, default="Disaster Management Command")
    sender_role = Column(String(50), nullable=False, default="admin")
    is_emergency_broadcast = Column(Boolean, default=False, index=True)
    expiry_time = Column(DateTime(timezone=True), nullable=True)
    acknowledged_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class AlertAuditLog(Base):
    __tablename__ = "alert_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    action = Column(String(50), nullable=False, index=True)  # TRIGGERED, MANUAL_SOS, STOPPED, ACKNOWLEDGED, MUTED
    performed_by = Column(String(255), nullable=False, default="system")
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    type = Column(String(100), default="Government", index=True)
    address = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    district = Column(String(255), index=True, nullable=True)
    state = Column(String(255), index=True, nullable=True)
    phone = Column(String(50), nullable=True)
    emergency_status = Column(String(50), default="OPEN", index=True)  # OPEN, LIMITED, FULL, EMERGENCY_ONLY, CLOSED, UNKNOWN
    operational_status = Column(String(50), default="OPEN", index=True) # OPEN, LIMITED, FULL, EMERGENCY_ONLY, CLOSED, UNKNOWN
    specialization = Column(String(255), default="General & Trauma Response")
    data_source = Column(String(100), default="Hospital Management System") # Google Maps / Places, Hospital Management System, Hospital API
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    location_point = Column(SpatialPoint, nullable=True)

    capacity = relationship("HospitalCapacity", back_populates="hospital", uselist=False, cascade="all, delete-orphan")
    updates = relationship("HospitalUpdate", back_populates="hospital", cascade="all, delete-orphan")
    hospital_users = relationship("HospitalUser", back_populates="hospital", cascade="all, delete-orphan")
    emergency_requests = relationship("EmergencyRequest", back_populates="hospital", cascade="all, delete-orphan")
    patients = relationship("HospitalPatient", back_populates="hospital", cascade="all, delete-orphan")
    status_history = relationship("HospitalStatusHistory", back_populates="hospital", cascade="all, delete-orphan")


class HospitalCapacity(Base):
    __tablename__ = "hospital_capacity"
    __table_args__ = (
        CheckConstraint("occupied_beds <= total_beds", name="check_hospital_beds_limit"),
        CheckConstraint("occupied_beds >= 0", name="check_hospital_beds_positive"),
        CheckConstraint("occupied_icu <= total_icu", name="check_hospital_icu_limit"),
        CheckConstraint("occupied_icu >= 0", name="check_hospital_icu_positive"),
        CheckConstraint("occupied_emergency_beds <= total_emergency_beds", name="check_hospital_emergency_limit"),
        CheckConstraint("occupied_emergency_beds >= 0", name="check_hospital_emergency_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_beds = Column(Integer, default=100)
    occupied_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=100)
    
    total_icu = Column(Integer, default=20)
    occupied_icu = Column(Integer, default=0)
    available_icu = Column(Integer, default=20)

    total_emergency_beds = Column(Integer, default=30)
    occupied_emergency_beds = Column(Integer, default=0)
    available_emergency_beds = Column(Integer, default=30)

    isolation_beds = Column(Integer, default=10)
    
    total_ambulances = Column(Integer, default=5)
    available_ambulances = Column(Integer, default=5)
    busy_ambulances = Column(Integer, default=0)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(255), default="System Admin")

    hospital = relationship("Hospital", back_populates="capacity")


class HospitalUpdate(Base):
    __tablename__ = "hospital_updates"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False, default="Admin")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    hospital = relationship("Hospital", back_populates="updates")




class HospitalUser(Base):
    """Links a system User account (role='hospital') to a specific Hospital row."""
    __tablename__ = "hospital_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    # Registration/verification status
    verification_status = Column(String(50), default="VERIFIED", index=True)  # PENDING, VERIFIED, SUSPENDED, REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hospital = relationship("Hospital", back_populates="hospital_users")
    user = relationship("User")


class EmergencyRequest(Base):
    """Emergency medical request sent from the disaster system to a hospital."""
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g. ER-1025
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    location_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    patients_count = Column(Integer, default=1, nullable=False)
    medical_requirement = Column(String(255), default="Emergency Treatment")
    priority = Column(String(50), default="HIGH", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    distance_km = Column(Float, default=0.0)
    estimated_arrival_minutes = Column(Float, default=0.0)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, ACCEPTED, REJECTED, IN_PROGRESS, COMPLETED
    created_by = Column(String(255), default="System")
    created_by_role = Column(String(50), default="admin")  # admin, responder, system
    notes = Column(Text, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hospital = relationship("Hospital", back_populates="emergency_requests")
    patients = relationship("HospitalPatient", back_populates="emergency_request", cascade="all, delete-orphan")


class HospitalPatient(Base):
    """Privacy-conscious patient record linked to a hospital and emergency request."""
    __tablename__ = "hospital_patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(100), unique=True, index=True, nullable=False)  # e.g. PAT-2026-001
    emergency_request_id = Column(Integer, ForeignKey("emergency_requests.id", ondelete="SET NULL"), nullable=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    age_range = Column(String(50), nullable=True)  # e.g. "Adult (18-60)" — not exact age
    medical_priority = Column(String(50), default="MEDIUM", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    arrival_time = Column(DateTime(timezone=True), server_default=func.now())
    treatment_status = Column(String(50), default="WAITING", index=True)  # WAITING, ADMITTED, IN_TREATMENT, ICU, DISCHARGED, TRANSFERRED
    assigned_department = Column(String(100), nullable=True)
    discharge_status = Column(String(50), default="ACTIVE", index=True)  # ACTIVE, DISCHARGED, TRANSFERRED, DECEASED
    discharge_time = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hospital = relationship("Hospital", back_populates="patients")
    emergency_request = relationship("EmergencyRequest", back_populates="patients")


class HospitalStatusHistory(Base):
    """Audit log for hospital operational status changes."""
    __tablename__ = "hospital_status_history"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    updated_by = Column(String(255), nullable=False, default="hospital_user")
    updated_by_role = Column(String(50), default="hospital")
    reason = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    hospital = relationship("Hospital", back_populates="status_history")
