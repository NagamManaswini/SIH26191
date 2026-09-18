"""
Unit and Integration Tests for Milestone 9: Citizen Crowd-Sourcing.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.citizen_report import CitizenReport
from app.models.sensor import Sensor
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.user import User
from app.models.enums import CitizenReportType, VerificationStatus, UserRole, SensorType, SensorStatus
from app.core.security import get_password_hash, create_access_token
from app.services.citizen_verification_engine import citizen_verification_engine, calculate_distance_km

client = TestClient(app)


@pytest.fixture
def auth_tokens():
    """Create test users for role-based verification testing."""
    db = SessionLocal()
    try:
        # 1. Citizen user
        citizen = db.query(User).filter(User.email == "test.citizen@example.com").first()
        if not citizen:
            citizen = User(
                name="Citizen Observer",
                email="test.citizen@example.com",
                password_hash=get_password_hash("CitizenPass123!"),
                role=UserRole.CITIZEN
            )
            db.add(citizen)
            db.commit()
            db.refresh(citizen)

        # 2. Response Team user
        responder = db.query(User).filter(User.email == "test.responder@example.com").first()
        if not responder:
            responder = User(
                name="Disaster Responder",
                email="test.responder@example.com",
                password_hash=get_password_hash("ResponderPass123!"),
                role=UserRole.RESPONSE_TEAM
            )
            db.add(responder)
            db.commit()
            db.refresh(responder)

        citizen_token = create_access_token(user_id=citizen.id, email=citizen.email, role="CITIZEN")
        responder_token = create_access_token(user_id=responder.id, email=responder.email, role="RESPONSE_TEAM")

        return {
            "citizen_token": citizen_token,
            "responder_token": responder_token,
            "responder_id": responder.id
        }
    finally:
        db.close()


def test_distance_calculation_haversine():
    """Verify spherical distance calculation between coordinates."""
    # Kedarnath (30.7346, 79.0669) to Gaurikund (30.6517, 79.0289) is ~10 km
    dist = calculate_distance_km(30.7346, 79.0669, 30.6517, 79.0289)
    assert 8.0 <= dist <= 12.0


def test_sensor_correlation_engine_logic():
    """Verify sensor corroboration boosts confidence when matching sensor telemetry is in vicinity."""
    db = SessionLocal()
    try:
        # Create a test river sensor at (30.70, 79.05) with high water level
        test_sensor = Sensor(
            name="Test Verification Sensor",
            sensor_code=f"S-VERIF-{int(datetime.now().timestamp())}",
            sensor_type=SensorType.RIVER_LEVEL,
            latitude=30.70,
            longitude=79.05,
            elevation=1850.0,
            status=SensorStatus.ACTIVE
        )
        db.add(test_sensor)
        db.commit()
        db.refresh(test_sensor)

        river_reading = RiverReading(
            sensor_id=test_sensor.id,
            water_level_m=4.2, # critical stage
            flow_rate=210.0,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(river_reading)
        db.commit()

        # Corroborate a RIVER_RISING report nearby (30.71, 79.06)
        corr = citizen_verification_engine.correlate_report_with_sensors(
            db=db,
            latitude=30.71,
            longitude=79.06,
            report_type=CitizenReportType.RIVER_RISING,
            has_image=True
        )

        assert corr["confidence_score"] >= 65.0
        assert corr["nearby_sensors_count"] >= 1
        assert corr["corroborating_sensors_count"] >= 1
        assert any("Critical stage" in r for r in corr["matching_reasons"])
    finally:
        db.close()


def test_submit_citizen_report_api():
    """Verify POST /api/reports creates a new report and computes initial confidence."""
    payload = {
        "report_type": "FLASH_FLOOD",
        "description": "Massive water torrent overflowing road near Gaurikund bridge.",
        "latitude": 30.652,
        "longitude": 79.029,
        "image_url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/...",
    }

    resp = client.post("/api/reports", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] > 0
    assert data["report_type"] == "FLASH_FLOOD"
    assert data["verification_status"] == "PENDING"
    assert data["confidence_score"] is not None
    assert data["confidence_score"] > 0


def test_get_citizen_reports_and_filters():
    """Verify GET /api/reports returns list and handles query filters."""
    resp = client.get("/api/reports")
    assert resp.status_code == 200
    reports = resp.json()
    assert isinstance(reports, list)
    assert len(reports) > 0

    # Filter by status
    resp_pending = client.get("/api/reports?verification_status=PENDING")
    assert resp_pending.status_code == 200
    for r in resp_pending.json():
        assert r["verification_status"] == "PENDING"


def test_get_citizen_report_detail_api():
    """Verify GET /api/reports/{id} returns nearby sensors and matching reasons."""
    # First get existing report
    resp_list = client.get("/api/reports")
    assert resp_list.status_code == 200
    report_id = resp_list.json()[0]["id"]

    resp = client.get(f"/api/reports/{report_id}")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["id"] == report_id
    assert "nearby_sensors" in detail
    assert "matching_reasons" in detail
    assert "confidence_score" in detail

    # 404 for nonexistent report
    resp_404 = client.get("/api/reports/999999")
    assert resp_404.status_code == 404


def test_verify_citizen_report_rbac(auth_tokens):
    """Verify report verification is role-protected to Response Team/Admin."""
    # Get a pending report ID
    db = SessionLocal()
    try:
        rep = db.query(CitizenReport).filter(CitizenReport.verification_status == VerificationStatus.PENDING).first()
        if not rep:
            rep = CitizenReport(
                report_type=CitizenReportType.ROAD_BLOCKAGE,
                description="Test road blocked by rockfall",
                latitude=30.60,
                longitude=79.10,
                verification_status=VerificationStatus.PENDING
            )
            db.add(rep)
            db.commit()
            db.refresh(rep)
        target_id = rep.id
    finally:
        db.close()

    # 1. Unauthenticated request -> 401
    resp_unauth = client.post(f"/api/reports/{target_id}/verify", json={"verification_status": "VERIFIED"})
    assert resp_unauth.status_code == 401

    # 2. Citizen user -> 403 Forbidden
    resp_citizen = client.post(
        f"/api/reports/{target_id}/verify",
        headers={"Authorization": f"Bearer {auth_tokens['citizen_token']}"},
        json={"verification_status": "VERIFIED"}
    )
    assert resp_citizen.status_code == 403

    # 3. Response Team user -> 200 OK
    resp_responder = client.post(
        f"/api/reports/{target_id}/verify",
        headers={"Authorization": f"Bearer {auth_tokens['responder_token']}"},
        json={
            "verification_status": "VERIFIED",
            "verification_notes": "Field unit dispatched and corroborated road blockage."
        }
    )
    assert resp_responder.status_code == 200
    verified_data = resp_responder.json()
    assert verified_data["verification_status"] == "VERIFIED"
    assert verified_data["verification_notes"] == "Field unit dispatched and corroborated road blockage."


def test_map_citizen_reports_geojson():
    """Verify GET /api/map/citizen-reports attaches coordinates, report types, and confidence scores."""
    resp = client.get("/api/map/citizen-reports")
    assert resp.status_code == 200
    geojson = resp.json()
    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    if len(geojson["features"]) > 0:
        f = geojson["features"][0]
        assert f["geometry"]["type"] == "Point"
        assert "report_type" in f["properties"]
        assert "verification_status" in f["properties"]
        assert "confidence_score" in f["properties"]
