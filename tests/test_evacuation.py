"""
Unit and Integration Tests for Milestone 10: Evacuation Management & Safe Routing.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.evacuation import EvacuationCenter
from app.models.alert import Alert
from app.models.citizen_report import CitizenReport
from app.models.user import User
from app.models.enums import UserRole, AlertType, AlertSeverity, AlertStatus, CitizenReportType, VerificationStatus
from app.core.security import get_password_hash, create_access_token
from app.services.evacuation_routing_engine import evacuation_routing_engine

client = TestClient(app)


@pytest.fixture
def auth_tokens():
    """Create test users with different roles for evacuation management tests."""
    db = SessionLocal()
    try:
        # Admin user
        admin = db.query(User).filter(User.email == "test.admin_evac@example.com").first()
        if not admin:
            admin = User(
                name="Admin Evacuation Officer",
                email="test.admin_evac@example.com",
                password_hash=get_password_hash("AdminPass123!"),
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # Response Team user
        responder = db.query(User).filter(User.email == "test.responder_evac@example.com").first()
        if not responder:
            responder = User(
                name="Field Responder",
                email="test.responder_evac@example.com",
                password_hash=get_password_hash("ResponderPass123!"),
                role=UserRole.RESPONSE_TEAM
            )
            db.add(responder)
            db.commit()
            db.refresh(responder)

        # Citizen user
        citizen = db.query(User).filter(User.email == "test.citizen_evac@example.com").first()
        if not citizen:
            citizen = User(
                name="Evac Citizen",
                email="test.citizen_evac@example.com",
                password_hash=get_password_hash("CitizenPass123!"),
                role=UserRole.CITIZEN
            )
            db.add(citizen)
            db.commit()
            db.refresh(citizen)

        admin_token = create_access_token(user_id=admin.id, email=admin.email, role="ADMIN")
        responder_token = create_access_token(user_id=responder.id, email=responder.email, role="RESPONSE_TEAM")
        citizen_token = create_access_token(user_id=citizen.id, email=citizen.email, role="CITIZEN")

        return {
            "admin_token": admin_token,
            "responder_token": responder_token,
            "citizen_token": citizen_token
        }
    finally:
        db.close()


def test_get_evacuation_centers_api():
    """Verify GET /api/evacuation/centers returns shelters with capacity and occupancy metrics."""
    # Ensure at least one center in DB
    db = SessionLocal()
    try:
        c = db.query(EvacuationCenter).first()
        if not c:
            c = EvacuationCenter(
                name="Guptkashi High Ridge Community Center",
                latitude=30.5230,
                longitude=79.0760,
                capacity=500,
                current_occupancy=120,
                is_active=True,
                district="Rudraprayag",
                elevation_m=2200.0,
                contact_number="+91-1364-267890",
                facilities="Medical station, 300 emergency beds, high-capacity generator"
            )
            db.add(c)
            db.commit()
            db.refresh(c)
        center_id = c.id
    finally:
        db.close()

    resp = client.get("/api/evacuation/centers")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    found = next((item for item in data if item["id"] == center_id), None)
    assert found is not None
    assert "available_capacity" in found
    assert "occupancy_percentage" in found
    assert found["available_capacity"] >= 0


def test_create_and_update_evacuation_center_rbac(auth_tokens):
    """Verify RBAC rules for creating and editing evacuation shelters."""
    new_center_payload = {
        "name": "Joshimath High School Shelter",
        "latitude": 30.5560,
        "longitude": 79.5630,
        "capacity": 350,
        "current_occupancy": 0,
        "is_active": True,
        "district": "Chamoli",
        "elevation_m": 2400.0,
        "contact_number": "+91-1372-222333",
        "facilities": "Food supplies, emergency warm blankets, satellite comms"
    }

    # 1. Unauthenticated creation -> 401
    resp_unauth = client.post("/api/evacuation/centers", json=new_center_payload)
    assert resp_unauth.status_code == 401

    # 2. Citizen user creation -> 403
    resp_citizen = client.post(
        "/api/evacuation/centers",
        headers={"Authorization": f"Bearer {auth_tokens['citizen_token']}"},
        json=new_center_payload
    )
    assert resp_citizen.status_code == 403

    # 3. Admin creation -> 201
    resp_admin = client.post(
        "/api/evacuation/centers",
        headers={"Authorization": f"Bearer {auth_tokens['admin_token']}"},
        json=new_center_payload
    )
    assert resp_admin.status_code == 201
    created = resp_admin.json()
    assert created["name"] == "Joshimath High School Shelter"
    created_id = created["id"]

    # 4. Response Team updating occupancy -> 200
    resp_update = client.put(
        f"/api/evacuation/centers/{created_id}",
        headers={"Authorization": f"Bearer {auth_tokens['responder_token']}"},
        json={"current_occupancy": 85}
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["current_occupancy"] == 85
    assert updated["available_capacity"] == 350 - 85


def test_get_nearest_evacuation_centers_api():
    """Verify GET /api/evacuation/nearest computes distance and sorts by proximity."""
    resp = client.get("/api/evacuation/nearest?latitude=30.6517&longitude=79.0289&limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "distance_km" in data[0]
    assert "safety_score" in data[0]
    # Ensure sorted by distance ascending
    if len(data) > 1:
        assert data[0]["distance_km"] <= data[1]["distance_km"]


def test_calculate_safe_evacuation_route_api():
    """Verify GET /api/evacuation/routes calculates safe path, turn steps, and elevation profile."""
    resp = client.get("/api/evacuation/routes?origin_lat=30.6517&origin_lon=79.0289")
    assert resp.status_code == 200
    route = resp.json()
    assert "total_distance_km" in route
    assert "estimated_walking_time_min" in route
    assert "estimated_driving_time_min" in route
    assert "waypoints" in route
    assert len(route["waypoints"]) >= 2
    assert "elevation_profile" in route
    assert len(route["elevation_profile"]) >= 2
    assert "turn_by_turn_steps" in route
    assert len(route["turn_by_turn_steps"]) > 0
    assert "hazard_avoidance_logs" in route


def test_hazard_avoidance_routing_detour():
    """Verify routing engine applies detour when a hazard or blocked road is on the trajectory."""
    db = SessionLocal()
    try:
        # Create an active emergency alert right in path
        alert = Alert(
            alert_type=AlertType.FLASH_FLOOD,
            severity=AlertSeverity.EMERGENCY,
            title="Obstacle Test Inundation Zone",
            message="Impassable flash flood barrier",
            latitude=30.58,
            longitude=79.05,
            radius_km=3.0,
            status=AlertStatus.ACTIVE
        )
        db.add(alert)

        # Create destination center
        dest_center = EvacuationCenter(
            name="Test Detour High Ground Center",
            latitude=30.50,
            longitude=79.08,
            capacity=400,
            current_occupancy=50,
            is_active=True
        )
        db.add(dest_center)
        db.commit()
        db.refresh(dest_center)

        # Calculate route from origin (30.65, 79.02)
        route = evacuation_routing_engine.calculate_safe_evacuation_route(
            db=db,
            origin_lat=30.65,
            origin_lon=79.02,
            destination_center=dest_center
        )

        assert route["total_distance_km"] > 0
        assert len(route["hazard_avoidance_logs"]) > 0
        assert any("Avoided" in log for log in route["hazard_avoidance_logs"])
    finally:
        db.close()
