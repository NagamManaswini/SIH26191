"""Seed Initial Real Hospitals and Capacity Data across Major Sectors."""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, init_db
from backend.app.models.entities import Hospital, HospitalCapacity, HospitalUpdate

SEED_HOSPITALS = [
    {
        "hospital_id": "HOSP_CHN_001",
        "name": "Rajiv Gandhi Government General Hospital",
        "type": "Government",
        "address": "EVR Periyar Salai, Park Town, Chennai, Tamil Nadu 600003",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "district": "Chennai",
        "state": "Tamil Nadu",
        "phone": "+91 44 2530 5000",
        "emergency_status": "OPEN",
        "operational_status": "OPEN",
        "specialization": "Trauma & Emergency Care, Multi-Specialty",
        "data_source": "Government Health Portal",
        "capacity": {
            "total_beds": 500,
            "occupied_beds": 350,
            "total_icu": 60,
            "occupied_icu": 42,
            "total_emergency_beds": 45,
            "occupied_emergency_beds": 20,
            "isolation_beds": 25,
            "total_ambulances": 12,
            "available_ambulances": 8,
        },
    },
    {
        "hospital_id": "HOSP_CHN_002",
        "name": "Apollo Main Hospital Chennai",
        "type": "Private",
        "address": "21 Greams Lane, Thousand Lights, Chennai, Tamil Nadu 600006",
        "latitude": 13.0604,
        "longitude": 80.2496,
        "district": "Chennai",
        "state": "Tamil Nadu",
        "phone": "+91 44 2829 0200",
        "emergency_status": "OPEN",
        "operational_status": "OPEN",
        "specialization": "Cardiology, Critical Emergency & Trauma",
        "data_source": "Hospital Management System",
        "capacity": {
            "total_beds": 600,
            "occupied_beds": 480,
            "total_icu": 80,
            "occupied_icu": 70,
            "total_emergency_beds": 50,
            "occupied_emergency_beds": 38,
            "isolation_beds": 30,
            "total_ambulances": 15,
            "available_ambulances": 5,
        },
    },
    {
        "hospital_id": "HOSP_CHN_003",
        "name": "Kilpauk Medical College Hospital",
        "type": "Public Medical College",
        "address": "822 Poonamallee High Rd, Kilpauk, Chennai, Tamil Nadu 600010",
        "latitude": 13.0784,
        "longitude": 80.2429,
        "district": "Chennai",
        "state": "Tamil Nadu",
        "phone": "+91 44 2836 4951",
        "emergency_status": "OPEN",
        "operational_status": "OPEN",
        "specialization": "Burns, Plastic Surgery & Disaster Trauma",
        "data_source": "Government Health Portal",
        "capacity": {
            "total_beds": 400,
            "occupied_beds": 290,
            "total_icu": 40,
            "occupied_icu": 28,
            "total_emergency_beds": 35,
            "occupied_emergency_beds": 15,
            "isolation_beds": 20,
            "total_ambulances": 8,
            "available_ambulances": 4,
        },
    },
    {
        "hospital_id": "HOSP_VSKP_001",
        "name": "King George Hospital (KGH)",
        "type": "District Hospital",
        "address": "Maharanipeta, Visakhapatnam, Andhra Pradesh 530002",
        "latitude": 17.7091,
        "longitude": 83.3031,
        "district": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "phone": "+91 891 256 4891",
        "emergency_status": "OPEN",
        "operational_status": "OPEN",
        "specialization": "General Medicine, Emergency Trauma Centre",
        "data_source": "Hospital Management System",
        "capacity": {
            "total_beds": 450,
            "occupied_beds": 310,
            "total_icu": 50,
            "occupied_icu": 35,
            "total_emergency_beds": 40,
            "occupied_emergency_beds": 18,
            "isolation_beds": 20,
            "total_ambulances": 10,
            "available_ambulances": 6,
        },
    },
    {
        "hospital_id": "HOSP_WAY_001",
        "name": "Wayanad District Hospital Mananthavady",
        "type": "District Hospital",
        "address": "Mananthavady, Wayanad, Kerala 670645",
        "latitude": 11.8028,
        "longitude": 76.0034,
        "district": "Wayanad",
        "state": "Kerala",
        "phone": "+91 4935 240 223",
        "emergency_status": "EMERGENCY_ONLY",
        "operational_status": "LIMITED",
        "specialization": "Landslide Emergency & Community Trauma",
        "data_source": "District Disaster Portal",
        "capacity": {
            "total_beds": 250,
            "occupied_beds": 210,
            "total_icu": 25,
            "occupied_icu": 22,
            "total_emergency_beds": 30,
            "occupied_emergency_beds": 28,
            "isolation_beds": 15,
            "total_ambulances": 6,
            "available_ambulances": 2,
        },
    },
]


def seed_hospitals():
    init_db()
    db = SessionLocal()
    print("=" * 60)
    print("🌱 SEEDING INITIAL HOSPITAL RECORDS AND CAPACITY METRICS")
    print("=" * 60)

    count = 0
    for h_data in SEED_HOSPITALS:
        cap_data = h_data.pop("capacity")
        existing = db.query(Hospital).filter(Hospital.hospital_id == h_data["hospital_id"]).first()

        if not existing:
            h = Hospital(**h_data)
            db.add(h)
            db.commit()
            db.refresh(h)

            tot_b = cap_data["total_beds"]
            occ_b = cap_data["occupied_beds"]
            tot_i = cap_data["total_icu"]
            occ_i = cap_data["occupied_icu"]
            tot_e = cap_data["total_emergency_beds"]
            occ_e = cap_data["occupied_emergency_beds"]
            tot_a = cap_data["total_ambulances"]
            avail_a = cap_data["available_ambulances"]

            cap = HospitalCapacity(
                hospital_id=h.id,
                total_beds=tot_b,
                occupied_beds=occ_b,
                available_beds=max(0, tot_b - occ_b),
                total_icu=tot_i,
                occupied_icu=occ_i,
                available_icu=max(0, tot_i - occ_i),
                total_emergency_beds=tot_e,
                occupied_emergency_beds=occ_e,
                available_emergency_beds=max(0, tot_e - occ_e),
                isolation_beds=cap_data.get("isolation_beds", 10),
                total_ambulances=tot_a,
                available_ambulances=avail_a,
                busy_ambulances=max(0, tot_a - avail_a),
                updated_by="System Seed Script",
            )
            db.add(cap)

            audit = HospitalUpdate(
                hospital_id=h.id,
                field_name="initial_creation",
                old_value=None,
                new_value=f"Seeded hospital {h.name} with capacity",
                updated_by="System Seed Script",
            )
            db.add(audit)
            db.commit()
            count += 1
            print(f"  + Seeded Hospital: {h.name} ({h.hospital_id}) - {h.district}")
        else:
            print(f"  . Hospital {existing.name} ({existing.hospital_id}) already exists.")

    print("=" * 60)
    print(f"🎉 Hospital seeding complete! Added {count} new hospital(s).")
    print("=" * 60)
    db.close()


if __name__ == "__main__":
    seed_hospitals()
