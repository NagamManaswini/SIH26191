"""Unit tests for Dynamic Hospital Management and Emergency Response endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_hospitals():
    response = client.get("/api/v1/hospitals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_hospital_recommendation():
    payload = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "medical_need": "emergency",
        "patients": 10,
        "max_radius_km": 50.0,
    }
    response = client.post("/api/v1/hospitals/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_hospital" in data
    assert "alternatives" in data


def test_create_and_update_hospital_capacity():
    # 1. Create a new hospital with admin header
    h_payload = {
        "hospital_id": "TEST_HOSP_999",
        "name": "Test Emergency Trauma Care",
        "type": "Specialty Hospital",
        "latitude": 13.0900,
        "longitude": 80.2800,
        "district": "Chennai",
        "state": "Tamil Nadu",
        "phone": "+91 99999 88888",
        "emergency_status": "OPEN",
        "operational_status": "OPEN",
        "specialization": "Trauma",
        "capacity": {
            "total_beds": 100,
            "occupied_beds": 20,
            "total_icu": 15,
            "occupied_icu": 5,
            "total_emergency_beds": 20,
            "occupied_emergency_beds": 5,
            "total_ambulances": 5,
            "available_ambulances": 5,
        },
    }

    res_create = client.post("/api/v1/hospitals", json=h_payload, headers={"X-User-Role": "admin"})
    assert res_create.status_code in [201, 400]  # Created or already exists
    if res_create.status_code == 201:
        h_data = res_create.json()
        h_id = h_data["id"]

        # 2. Update capacity as admin
        cap_update = {
            "occupied_beds": 50,
            "occupied_icu": 10,
            "occupied_emergency_beds": 15,
            "updated_by": "Test Suite Admin",
        }
        res_cap = client.patch(f"/api/v1/hospitals/{h_id}/capacity", json=cap_update, headers={"X-User-Role": "admin"})
        assert res_cap.status_code == 200
        updated_cap = res_cap.json()
        assert updated_cap["available_beds"] == 50
        assert updated_cap["available_icu"] == 5
        assert updated_cap["available_emergency_beds"] == 5

        # 3. Validation failure check (occupied > total)
        bad_cap = {"occupied_beds": 200, "total_beds": 100}
        res_bad = client.patch(f"/api/v1/hospitals/{h_id}/capacity", json=bad_cap, headers={"X-User-Role": "admin"})
        assert res_bad.status_code == 400

        # 4. Role Authorization check (citizen role rejected for mutating capacity)
        res_auth = client.patch(f"/api/v1/hospitals/{h_id}/capacity", json={"occupied_beds": 30}, headers={"X-User-Role": "user"})
        assert res_auth.status_code == 403
