"""Script to seed sample shelter and shelter resource data into the database for Phase 4 demonstration."""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.database import SessionLocal, init_db
from backend.app.models.entities import Shelter, ShelterResource
from backend.app.utils.geo import coords_to_point_wkt


def seed_demo_shelters():
    """Seed sample shelters with capacity, resources, and ratings."""
    init_db()
    db = SessionLocal()

    try:
        if db.query(Shelter).count() > 0:
            print("Shelter database already contains records. Skipping seed.")
            return

        demo_data = [
            {
                "name": "Central High School Relief Shelter",
                "address": "12 Sector A Main Highway",
                "capacity": 500,
                "current_occupancy": 120,
                "status": "active",
                "contact_number": "+91-9876543210",
                "accessibility_rating": 0.90,
                "structural_safety_rating": 0.95,
                "lon": 72.87,
                "lat": 19.07,
                "resources": {
                    "water_supply_days": 10.0,
                    "food_supply_days": 8.0,
                    "medical_kits": 60,
                    "power_backup": True,
                    "sanitation_facilities": 25,
                },
            },
            {
                "name": "North Ridge Community Stadium",
                "address": "88 Foothill Expressway",
                "capacity": 1200,
                "current_occupancy": 850,
                "status": "active",
                "contact_number": "+91-9876543211",
                "accessibility_rating": 0.85,
                "structural_safety_rating": 0.90,
                "lon": 72.92,
                "lat": 19.13,
                "resources": {
                    "water_supply_days": 5.0,
                    "food_supply_days": 6.0,
                    "medical_kits": 40,
                    "power_backup": True,
                    "sanitation_facilities": 30,
                },
            },
            {
                "name": "Valley Primary Health Center",
                "address": "4 Riverside Avenue",
                "capacity": 200,
                "current_occupancy": 200,  # FULL shelter
                "status": "full",
                "contact_number": "+91-9876543212",
                "accessibility_rating": 0.70,
                "structural_safety_rating": 0.80,
                "lon": 72.86,
                "lat": 19.06,
                "resources": {
                    "water_supply_days": 3.0,
                    "food_supply_days": 4.0,
                    "medical_kits": 80,
                    "power_backup": False,
                    "sanitation_facilities": 10,
                },
            },
        ]

        for s in demo_data:
            res_data = s.pop("resources")
            lon, lat = s.pop("lon"), s.pop("lat")
            wkt_loc = coords_to_point_wkt(lon, lat)

            shelter_obj = Shelter(location=wkt_loc, **s)
            db.add(shelter_obj)
            db.commit()
            db.refresh(shelter_obj)

            resource_obj = ShelterResource(shelter_id=shelter_obj.id, **res_data)
            db.add(resource_obj)
            db.commit()

        print("Successfully seeded sample shelter data with capacity and resources!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_shelters()
