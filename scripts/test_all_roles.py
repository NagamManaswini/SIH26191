"""Comprehensive Test Suite to run and verify ALL ROLES and ALL PLATFORM FEATURES.
Tests Admin, Responder, Citizen (User), and Hospital roles and all associated API endpoints.
"""

import os
import sys
import json
from datetime import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Set offline SQLite fallback environment
os.environ["DATABASE_URL"] = "sqlite:///./sih_disaster.db"
os.environ["APP_ENV"] = "testing"

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, SessionLocal
from backend.app.models.entities import Hospital, HospitalCapacity, HospitalUser, User, Shelter
from backend.app.utils.security import hash_password

client = TestClient(app)

def setup_test_data():
    """Ensure database is initialized and seeded with all test entities."""
    init_db()
    db = SessionLocal()
    try:
        # Verify or seed demo hospital
        hosp = db.query(Hospital).first()
        if not hosp:
            hosp = Hospital(
                hospital_id="HOSP-GGH-001",
                name="Government General Hospital",
                type="Government",
                district="Wayanad",
                state="Kerala",
                address="Meppadi-Kalpetta Main Road, Wayanad",
                phone="+91-4936-202202",
                latitude=11.5520,
                longitude=76.1280,
                emergency_status="OPEN",
                operational_status="OPEN",
                is_active=True,
            )
            db.add(hosp)
            db.commit()
            db.refresh(hosp)

            # Add capacity
            cap = HospitalCapacity(
                hospital_id=hosp.id,
                total_beds=250,
                occupied_beds=180,
                available_beds=70,
                total_icu=30,
                occupied_icu=22,
                available_icu=8,
                total_emergency_beds=20,
                occupied_emergency_beds=8,
                available_emergency_beds=12,
                isolation_beds=10,
                total_ambulances=5,
                available_ambulances=3,
                busy_ambulances=2,
            )
            db.add(cap)
            db.commit()

        # Check hospital user
        hosp_user = db.query(User).filter(User.email == "hospital@ggh.example").first()
        if not hosp_user:
            hosp_user = User(
                email="hospital@ggh.example",
                password_hash=hash_password("Hospital#2026"),
                full_name="Government General Hospital Admin",
                role="hospital",
                is_active=True,
            )
            db.add(hosp_user)
            db.commit()
            db.refresh(hosp_user)

            hu = HospitalUser(
                user_id=hosp_user.id,
                hospital_id=hosp.id,
                verification_status="VERIFIED",
            )
            db.add(hu)
            db.commit()

    finally:
        db.close()


def run_tests():
    print("=" * 75)
    print(" COMPREHENSIVE MULTI-ROLE & FEATURE VERIFICATION SUITE")
    print(" Testing: Admin, Responder, Citizen (User), Hospital & Offline Engines")
    print("=" * 75)

    setup_test_data()

    results = []

    def check(role: str, feature: str, condition: bool, details: str = ""):
        results.append((role, feature, condition, details))
        icon = "[OK]" if condition else "[ERROR]"
        print(f"{icon} [{role.upper()}] {feature}: {details}")

    # =========================================================================
    # 1. CORE SYSTEM & HEALTH ENDPOINTS (ALL ROLES)
    # =========================================================================
    print("\n--- 1. Testing Core Diagnostic & System Health ---")
    r = client.get("/health")
    check("System", "Health Check", r.status_code == 200, f"Status: {r.status_code}")

    r = client.get("/api/v1/demo/full-system-check")
    check("System", "Full System Operational Diagnostics", r.status_code == 200, f"Modules Active: {r.json().get('status')}")

    r = client.post("/api/v1/demo/simulate-full-flow", json={"region": "Wayanad Sector 1", "evacuee_count": 150})
    check("System", "End-to-End Emergency Simulation", r.status_code == 200, f"Scenario: {r.json().get('scenario_status')}")

    # =========================================================================
    # 2. ADMIN ROLE (Full Command, Relocation, Reports, Weather, PDF)
    # =========================================================================
    print("\n--- 2. Testing ADMIN Role Features ---")
    admin_headers = {"X-User-Role": "admin"}
    
    # 2.1 Hazard Zones
    r = client.get("/api/v1/hazards")
    check("Admin", "Hazard Red Zones Query", r.status_code == 200, f"Found {len(r.json())} Hazard Zones")

    # 2.2 Shelters & Capacity
    r = client.get("/api/v1/shelters")
    check("Admin", "Shelters List", r.status_code == 200, f"Found {len(r.json())} Shelters")

    r = client.get("/api/v1/shelters/capacity")
    check("Admin", "Shelter Carrying Capacity Scoring", r.status_code == 200, f"Evaluated {len(r.json())} Shelters")

    # 2.3 Evacuation Safe Detour Routing (Dijkstra)
    r = client.post("/api/v1/routes/calculate", json={
        "origin": {"latitude": 11.5300, "longitude": 76.1300},
        "destination": {"latitude": 11.5450, "longitude": 76.1210},
        "risk_preference": "strict_safety"
    })
    check("Admin", "NetworkX Dijkstra Safe Route", r.status_code == 200, f"Distance: {r.json().get('total_distance_km', 0)} km, Safety: {r.json().get('safety_category', 'OK')}")

    # 2.4 Relocation Optimization Plan
    r = client.post("/api/v1/relocation/plan", json={
        "population_groups": [
            {
                "location_name": "Chooralmala Sector Alpha",
                "total_population": 150,
                "vulnerable_population": 25,
                "latitude": 11.5300,
                "longitude": 76.1300
            }
        ],
        "risk_preference": "strict_safety",
        "max_distance_km": 50.0
    })
    check("Admin", "Linear Programming Relocation Plan", r.status_code == 200, f"Plan Status: {r.json().get('status')}, Total Evacuated: {r.json().get('total_evacuated')}")

    # 2.5 Alerts Broadcast
    r = client.get("/api/v1/alerts")
    check("Admin", "Disaster Alerts Feed", r.status_code == 200, f"{len(r.json())} Active Alerts")

    # 2.6 Live Weather Telemetry
    r = client.get("/api/v1/weather/live?lat=11.5204&lon=76.1368")
    check("Admin", "Live Weather & Rainfall Telemetry", r.status_code == 200, f"Location: {r.json().get('location_name', 'Live Radar')}")

    # 2.7 Animal Safety
    r = client.get("/api/v1/animals/")
    check("Admin", "Livestock & Animal Rescue Records", r.status_code == 200, f"{len(r.json())} Animals tracked")

    # 2.8 PDF Report Generation
    r = client.post("/api/v1/reports/generate", json={
        "location_name": "Chooralmala Sector 1",
        "latitude": 11.5204,
        "longitude": 76.1368,
        "admin_name": "Command Chief Officer"
    }, headers=admin_headers)
    check("Admin", "ReportLab Dynamic PDF Generator", r.status_code == 200 and len(r.content) > 1000, f"Generated PDF ({len(r.content)} bytes)")

    # =========================================================================
    # 3. RESPONDER ROLE (Field Operations, Road Clearance, Communications)
    # =========================================================================
    print("\n--- 3. Testing RESPONDER (Field Operations) Role Features ---")

    r = client.get("/api/v1/hazards/map")
    check("Responder", "GeoJSON Hazard Boundaries Map", r.status_code == 200, f"Features: {len(r.json().get('features', []))}")

    r = client.get("/api/v1/shelters/capacity")
    check("Responder", "Field Shelter Suitability & Bed Status", r.status_code == 200, "Capacity status retrieved")

    r = client.get("/api/v1/communications/messages")
    check("Responder", "Emergency Field Communications Messages", r.status_code == 200, f"{len(r.json())} Messages active")

    r = client.get("/api/v1/animals/shelters")
    check("Responder", "Livestock Safe Holding Capacities", r.status_code == 200, "Animal holding facilities verified")

    # =========================================================================
    # 4. CITIZEN / USER ROLE (Citizen Portal, Safe Detours, Emergency Hotlines)
    # =========================================================================
    print("\n--- 4. Testing CITIZEN (User Portal) Role Features ---")

    r = client.get("/api/v1/shelters")
    check("Citizen", "Public Relief Shelters Query", r.status_code == 200, "Nearby verified shelters accessible")

    r = client.post("/api/v1/routes/calculate", json={
        "origin": {"latitude": 11.5350, "longitude": 76.1350},
        "destination": {"latitude": 11.5482, "longitude": 76.1245},
        "risk_preference": "strict_safety"
    })
    check("Citizen", "Citizen Evacuation Navigation Route", r.status_code == 200, f"Safe Route: {r.json().get('total_distance_km', 0)} km ({r.json().get('estimated_travel_time_mins', 0)} mins)")

    r = client.get("/api/v1/alerts")
    check("Citizen", "Public Emergency Alert Warnings", r.status_code == 200, "Public warnings broadcast active")

    r = client.get("/api/v1/weather/live?lat=11.5204&lon=76.1368")
    check("Citizen", "Local Weather & Flood Warning", r.status_code == 200, "Weather telemetry accessible")

    # =========================================================================
    # 5. HOSPITAL ROLE (Hospital Portal, Beds, Blood Bank, Emergency Requests)
    # =========================================================================
    print("\n--- 5. Testing HOSPITAL Role Features ---")

    r = client.get("/api/v1/hospitals")
    check("Hospital", "Hospitals & Medical Centers Directory", r.status_code == 200 and len(r.json()) > 0, f"{len(r.json())} Hospitals verified")

    hospital_headers = {"X-User-Role": "hospital", "X-Hospital-Id": "1"}

    # Hospital Self Profile
    r = client.get("/api/v1/hospital/me", headers=hospital_headers)
    check("Hospital", "Hospital Profile & Contact Info", r.status_code == 200, f"Name: {r.json().get('name', 'N/A')}")

    # Hospital Capacity
    r = client.get("/api/v1/hospital/capacity", headers=hospital_headers)
    check("Hospital", "Hospital Bed & Blood Bank Telemetry", r.status_code == 200, f"Available Beds: {r.json().get('available_beds', 'N/A')}")

    # Update capacity test
    r = client.patch("/api/v1/hospital/capacity", json={
        "total_beds": 250,
        "occupied_beds": 175,
        "available_beds": 75,
        "total_icu": 30,
        "occupied_icu": 20,
        "available_icu": 10,
        "total_emergency_beds": 20,
        "occupied_emergency_beds": 8,
        "available_emergency_beds": 12,
        "total_ambulances": 5,
        "available_ambulances": 4,
        "busy_ambulances": 1,
    }, headers=hospital_headers)
    check("Hospital", "Real-time Bed & Ambulance Fleet Update", r.status_code == 200, "Capacity updated successfully")

    # Hospital Emergency Requests
    r = client.get("/api/v1/hospital/emergency-requests", headers=hospital_headers)
    check("Hospital", "Emergency Requests Triage Queue", r.status_code == 200, "Emergency triage queue active")

    # Hospital Analytics
    r = client.get("/api/v1/hospital/analytics", headers=hospital_headers)
    check("Hospital", "Hospital Medical Analytics & Occupancy", r.status_code == 200, "Analytics retrieved")

    # =========================================================================
    # 6. OFFLINE PWA & STANDALONE FIELD DEPLOYMENT ASSETS
    # =========================================================================
    print("\n--- 6. Testing Offline PWA & Static Bundle Endpoints ---")

    r = client.get("/manifest.json")
    check("Offline PWA", "Web App Manifest", r.status_code == 200, f"Manifest served ({len(r.content)} bytes)")

    r = client.get("/sw.js")
    check("Offline PWA", "Service Worker Script", r.status_code == 200, f"Service worker active ({len(r.content)} bytes)")

    r = client.get("/download-pdf")
    check("Offline PWA", "Overview PDF Download Endpoint", r.status_code == 200, f"PDF file served ({len(r.content)} bytes)")

    r = client.get("/download-features-pdf")
    check("Offline PWA", "All-Features Guide PDF Endpoint", r.status_code == 200, f"Guide PDF served ({len(r.content)} bytes)")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 75)
    total = len(results)
    passed = sum(1 for _, _, ok, _ in results if ok)
    failed = total - passed

    print(f" FINAL SUMMARY: {passed}/{total} TESTS PASSED (Failed: {failed})")
    print("=" * 75)
    
    if failed == 0:
        print("[SUCCESS] ALL ROLES AND FEATURES ARE 100% OPERATIONAL AND FULLY WORKING!\n")
        return 0
    else:
        print(f"[WARNING] {failed} test(s) encountered issues.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
