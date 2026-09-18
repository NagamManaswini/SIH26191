import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_command_center_overview_api():
    response = client.get("/api/command-center/overview")
    assert response.status_code == 200
    data = response.json()
    assert "active_emergencies" in data
    assert "critical_watersheds" in data
    assert "high_risk_zones" in data
    assert "active_alerts" in data
    assert "online_sensors" in data
    assert "offline_sensors" in data
    assert "citizen_reports" in data
    assert "people_at_risk" in data
    assert "threat_level" in data
    assert "system_readiness_pct" in data
    assert isinstance(data["people_at_risk"], int)

def test_command_center_timeline_api():
    response = client.get("/api/command-center/timeline?limit=15")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        event = data[0]
        assert "id" in event
        assert "event_type" in event
        assert "severity" in event
        assert "title" in event
        assert "timestamp" in event

def test_command_center_trends_api():
    response = client.get("/api/command-center/trends?time_window=24h")
    assert response.status_code == 200
    data = response.json()
    assert "time_window" in data
    assert "series" in data
    assert len(data["series"]) > 0
    first_pt = data["series"][0]
    assert "rainfall_mm" in first_pt
    assert "river_level_m" in first_pt
    assert "soil_moisture_pct" in first_pt
    assert "risk_score" in first_pt

def test_command_center_sensor_health_audit_api():
    response = client.get("/api/command-center/sensor-health")
    assert response.status_code == 200
    data = response.json()
    assert "total_sensors" in data
    assert "online_count" in data
    assert "offline_count" in data
    assert "battery_warnings_count" in data
    assert "signal_warnings_count" in data
    assert "sensors" in data
    assert len(data["sensors"]) == data["total_sensors"]
