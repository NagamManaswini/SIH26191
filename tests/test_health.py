import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.sensor import Sensor
from app.models.watershed import Watershed
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.evacuation import EvacuationCenter
from app.models.user import User

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "flash-flood-backend"

def test_db_health_check():
    response = client.get("/api/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "latency_ms" in data
    assert "dialect" in data

def test_sensors_api():
    response = client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10

def test_watersheds_api():
    response = client.get("/api/watersheds")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5

def test_sensor_readings_api():
    # Fetch first sensor
    sensors_resp = client.get("/api/sensors")
    assert sensors_resp.status_code == 200
    sensors = sensors_resp.json()
    first_sensor_id = sensors[0]["id"]

    # Test rainfall endpoint
    rain_resp = client.get(f"/api/sensors/{first_sensor_id}/readings/rainfall")
    assert rain_resp.status_code == 200

def test_database_counts():
    db = SessionLocal()
    try:
        assert db.query(Sensor).count() >= 10
        assert db.query(Watershed).count() >= 5
        assert db.query(RainfallReading).count() >= 20
        assert db.query(RiverReading).count() >= 20
        assert db.query(SoilMoistureReading).count() >= 10
        assert db.query(EvacuationCenter).count() >= 5
        assert db.query(User).count() >= 5
    finally:
        db.close()
