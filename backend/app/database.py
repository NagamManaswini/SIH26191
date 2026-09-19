"""Database Engine Setup with Automatic SQLite Fallback for Local Development & Testing."""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings


def _get_sqlite_fallback_url() -> str:
    """Determine safe SQLite URL depending on deployment environment (Vercel/Lambda vs Local)."""
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or (os.name != "nt" and os.path.exists("/tmp")):
        return "sqlite:////tmp/sih_disaster.db"
    return "sqlite:///./sih_disaster.db"


def _sanitize_and_resolve_db_url() -> str:
    """Resolve and sanitize PostgreSQL/SQLite connection URL from environment variables."""
    # Check possible env vars in order of priority (including Vercel Postgres env vars)
    raw_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or os.environ.get("DATABASE_PUBLIC_URL")
        or settings.DATABASE_URL
        or ""
    )

    raw_url = raw_url.strip().strip("'\"")

    if not raw_url:
        return _get_sqlite_fallback_url()

    # Normalize PostgreSQL URL scheme for SQLAlchemy 2.0+
    if raw_url.startswith("postgres://"):
        raw_url = "postgresql+psycopg2://" + raw_url[len("postgres://"):]
    elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+"):
        raw_url = "postgresql+psycopg2://" + raw_url[len("postgresql://"):]

    return raw_url


db_url = _sanitize_and_resolve_db_url()
connect_args = {}

# Test PostgreSQL availability; fallback to SQLite if PostgreSQL is unreachable or invalid URL
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    try:
        temp_engine = create_engine(db_url, connect_args={"connect_timeout": 2})
        with temp_engine.connect() as conn:
            pass
        temp_engine.dispose()
    except Exception as err:
        fallback_url = _get_sqlite_fallback_url()
        print(f"[WARNING] PostgreSQL connection check returned: {err}. Falling back to SQLite database ({fallback_url}).")
        db_url = fallback_url
        connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
except Exception as engine_err:
    print(f"[WARNING] Could not initialize engine with {db_url}: {engine_err}. Initializing fallback SQLite engine.")
    db_url = _get_sqlite_fallback_url()
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for providing database session to FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables safely and seed initial database records if empty."""
    try:
        import backend.app.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        print(f"[OK] Database initialized successfully using engine: {engine.url.drivername}")

        # Seed initial database records if empty
        db = SessionLocal()
        try:
            from backend.app.models.entities import Shelter, ShelterResource, HazardZone, Population, Alert

            if db.query(Shelter).count() == 0:
                print("[INIT] Seeding shelters table in database...")
                s1 = Shelter(
                    name="St. Joseph Higher Secondary School Shelter",
                    address="Meppadi Town, Wayanad, Kerala - 673577",
                    capacity=650,
                    current_occupancy=120,
                    status="active",
                    contact_number="+91-9447100101",
                    accessibility_rating=0.9,
                    structural_safety_rating=0.95,
                    location="POINT(76.1210 11.5450)",
                )
                s2 = Shelter(
                    name="Meppadi Community Hall & Relief Camp",
                    address="Near Main Bus Stand, Meppadi, Wayanad, Kerala - 673577",
                    capacity=500,
                    current_occupancy=85,
                    status="active",
                    contact_number="+91-9447100102",
                    accessibility_rating=0.85,
                    structural_safety_rating=0.88,
                    location="POINT(76.1245 11.5482)",
                )
                s3 = Shelter(
                    name="Government Primary Health Center Meppadi",
                    address="Hospital Road, Meppadi, Wayanad, Kerala - 673577",
                    capacity=250,
                    current_occupancy=40,
                    status="active",
                    contact_number="+91-9447100103",
                    accessibility_rating=0.95,
                    structural_safety_rating=0.92,
                    location="POINT(76.1260 11.5510)",
                )
                s4 = Shelter(
                    name="Wayanad Relief Auditorium",
                    address="Kalpetta Bypass Highway, Wayanad, Kerala - 673121",
                    capacity=1200,
                    current_occupancy=310,
                    status="active",
                    contact_number="+91-9447100104",
                    accessibility_rating=0.90,
                    structural_safety_rating=0.94,
                    location="POINT(76.0840 11.6080)",
                )
                db.add_all([s1, s2, s3, s4])
                db.commit()

                # Add shelter resources
                r1 = ShelterResource(shelter_id=s1.id, water_supply_days=7.0, food_supply_days=7.0, medical_kits=50, power_backup=True, sanitation_facilities=25)
                r2 = ShelterResource(shelter_id=s2.id, water_supply_days=5.0, food_supply_days=5.0, medical_kits=20, power_backup=True, sanitation_facilities=15)
                r3 = ShelterResource(shelter_id=s3.id, water_supply_days=4.0, food_supply_days=4.0, medical_kits=100, power_backup=True, sanitation_facilities=10)
                r4 = ShelterResource(shelter_id=s4.id, water_supply_days=10.0, food_supply_days=10.0, medical_kits=80, power_backup=True, sanitation_facilities=40)
                db.add_all([r1, r2, r3, r4])
                db.commit()
                print("[OK] Seeded 4 shelters and resource records.")

            if db.query(HazardZone).count() == 0:
                print("[INIT] Seeding hazard_zones table...")
                h1 = HazardZone(
                    name="Chooralmala Red Zone",
                    hazard_type="landslide",
                    risk_level="CRITICAL",
                    risk_score=0.92,
                    boundary="POLYGON((76.10 11.50, 76.16 11.50, 76.16 11.56, 76.10 11.56, 76.10 11.50))",
                )
                h2 = HazardZone(
                    name="Mundakkai High Risk Slope",
                    hazard_type="landslide",
                    risk_level="HIGH",
                    risk_score=0.78,
                    boundary="POLYGON((76.11 11.51, 76.15 11.51, 76.15 11.55, 76.11 11.55, 76.11 11.51))",
                )
                db.add_all([h1, h2])
                db.commit()
                print("[OK] Seeded hazard zones.")

            if db.query(Alert).count() == 0:
                print("[INIT] Seeding alerts table...")
                a1 = Alert(
                    title="RED LANDSLIDE WARNING — Wayanad (Chooralmala & Mundakkai)",
                    message="Extreme rainfall exceeding 340mm/24h recorded. Unstable soil condition detected on steep slopes.",
                    severity="CRITICAL",
                    affected_area="Wayanad Sector 1 (Chooralmala & Mundakkai)",
                    recommended_action="Immediate evacuation to St. Joseph Higher Secondary School Shelter or Meppadi Community Hall.",
                    status="ACTIVE",
                )
                a2 = Alert(
                    title="HEAVY RAINFALL ALERT — Idukki High Altitude Slopes",
                    message="Continuous downpour causing surface runoff accumulation. High risk of localized mudslides.",
                    severity="HIGH",
                    affected_area="Idukki District High Altitude Sector",
                    recommended_action="Citizens in low-lying slope valleys move to Idukki District Relief Center.",
                    status="ACTIVE",
                )
                a3 = Alert(
                    title="COASTAL FLOOD & HIGH TIDE ADVISORY — Ernakulam",
                    message="High coastal tide combined with river basin overflow. Low-lying urban streets experiencing waterlogging.",
                    severity="WARNING",
                    affected_area="Ernakulam Coastal Plain",
                    recommended_action="Avoid waterlogged roads and monitor official emergency broadcasts.",
                    status="ACTIVE",
                )
                db.add_all([a1, a2, a3])
                db.commit()
                print("[OK] Seeded emergency alerts.")

            from backend.app.models.entities import AnimalShelter, Animal, CommunicationMessage
            if db.query(AnimalShelter).count() == 0:
                print("[INIT] Seeding animal_shelters table...")
                ans1 = AnimalShelter(
                    name="North Valley Livestock Safe Holding Facility",
                    address="North Ridge Road, Wayanad Sector 2",
                    capacity=250,
                    current_occupancy=45,
                    supported_animal_types="cattle,goats,sheep,dogs,cats,poultry,other_livestock",
                    water_availability=True,
                    food_availability=True,
                    safety_status="SAFE",
                    location="POINT(76.1350 11.5600)",
                )
                ans2 = AnimalShelter(
                    name="Community Animal Rescue Center B",
                    address="Kalpetta Agricultural Complex, Wayanad Sector 3",
                    capacity=150,
                    current_occupancy=30,
                    supported_animal_types="cattle,goats,dogs,cats,poultry",
                    water_availability=True,
                    food_availability=True,
                    safety_status="SAFE",
                    location="POINT(76.0900 11.6150)",
                )
                db.add_all([ans1, ans2])
                db.commit()

                # Seed sample animals in Red Zone needing rescue
                an1 = Animal(
                    tag_id="ANIM-CATTLE-101",
                    owner_id="COMMUNITY-MEPPADI-01",
                    owner_name="Meppadi Dairy Cooperative",
                    animal_type="cattle",
                    name="Lakshmi Dairy Herd (15 Cattle)",
                    location_name="Chooralmala Red Zone Alpha",
                    emergency_status="AT_RISK",
                    rescue_status="PENDING",
                )
                an2 = Animal(
                    tag_id="ANIM-GOAT-202",
                    owner_id="RESIDENT-MUNDAKKAI-44",
                    owner_name="Ramesh Kumar",
                    animal_type="goats",
                    name="Mountain Goat Herd (8 Goats)",
                    location_name="Mundakkai High Risk Slope",
                    emergency_status="AT_RISK",
                    rescue_status="PENDING",
                )
                an3 = Animal(
                    tag_id="ANIM-PET-305",
                    owner_id="RESIDENT-MEPPADI-12",
                    owner_name="Anitha Nair",
                    animal_type="dogs",
                    name="Bruno (German Shepherd)",
                    location_name="Chooralmala Red Zone Alpha",
                    emergency_status="AT_RISK",
                    rescue_status="PENDING",
                )
                db.add_all([an1, an2, an3])
                db.commit()
                print("[OK] Seeded animal shelters and animal records.")

            if db.query(CommunicationMessage).count() == 0:
                print("[INIT] Seeding communication_messages table...")
                m1 = CommunicationMessage(
                    category="EMERGENCY",
                    title="CRITICAL EVACUATION ORDER — Chooralmala & Mundakkai",
                    message="Immediate evacuation advised for all residents in Zone Alpha. Proceed to St. Joseph Higher Secondary School Shelter via North Detour Route.",
                    target_area="Chooralmala & Mundakkai",
                    severity="CRITICAL",
                    sender_name="District Disaster Management Authority",
                    sender_role="admin",
                    is_emergency_broadcast=True,
                )
                m2 = CommunicationMessage(
                    category="ANIMAL_SAFETY",
                    title="Livestock & Pet Evacuation Assistance Point Ready",
                    message="Farmers and pet owners in Red Zone Alpha: Animal rescue units deployed at Community Center C. Livestock safe holding ready at North Valley Facility.",
                    target_area="Wayanad Sector 1",
                    severity="HIGH",
                    sender_name="Veterinary & Animal Safety Corps",
                    sender_role="admin",
                    is_emergency_broadcast=True,
                )
                db.add_all([m1, m2])
                db.commit()
                print("[OK] Seeded initial community communication messages.")

            # Clean database duplicates
            try:
                # 1. Deduplicate shelters by name
                all_shelters = db.query(Shelter).all()
                seen_shelter_names = set()
                for s in all_shelters:
                    if s.name in seen_shelter_names:
                        db.delete(s)
                    else:
                        seen_shelter_names.add(s.name)

                # 2. Deduplicate animals by tag_id
                all_animals = db.query(Animal).all()
                seen_tags = set()
                for an in all_animals:
                    if an.tag_id in seen_tags:
                        db.delete(an)
                    else:
                        seen_tags.add(an.tag_id)

                db.commit()
            except Exception as clean_err:
                print(f"[NOTE] Database cleanup note: {clean_err}")

            # Seed demo hospital user account (role=hospital)
            from backend.app.models.entities import User, HospitalUser, Hospital as HospitalModel
            from backend.app.utils.security import hash_password as _hash_pw
            existing_hospital_user = db.query(User).filter(User.email == "hospital@ggh.example").first()
            if not existing_hospital_user:
                first_hospital = db.query(HospitalModel).filter(HospitalModel.is_active == True).first()
                if first_hospital:
                    hosp_user = User(
                        email="hospital@ggh.example",
                        password_hash=_hash_pw("Hospital#2026"),
                        full_name="Government General Hospital Admin",
                        role="hospital",
                        is_active=True,
                    )
                    db.add(hosp_user)
                    db.commit()
                    db.refresh(hosp_user)
                    hu = HospitalUser(
                        user_id=hosp_user.id,
                        hospital_id=first_hospital.id,
                        verification_status="VERIFIED",
                    )
                    db.add(hu)
                    db.commit()
                    print(f"[OK] Seeded demo hospital user: hospital@ggh.example → Hospital '{first_hospital.name}'")

        finally:
            db.close()

    except Exception as e:
        print(f"[WARNING] Database initialization note: {e}")
