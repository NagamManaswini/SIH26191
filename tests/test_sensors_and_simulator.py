import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.models.enums import SensorType, SensorStatus

client = TestClient(app)

def test_get_all_sensors():
    """Test GET /api/sensors returns list of sensors with enriched metadata."""
    response = client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    first = data[0]
    assert "sensor_code" in first
    assert "name" in first
    assert "sensor_type" in first
    assert "battery_level" in first
    assert "status" in first

def test_filter_sensors_by_type():
    """Test GET /api/sensors?sensor_type=RAINFALL filters properly."""
    response = client.get("/api/sensors?sensor_type=RAINFALL")
    assert response.status_code == 200
    data = response.json()
    for s in data:
        assert s["sensor_type"] == "RAINFALL"

def test_filter_sensors_by_status():
    """Test GET /api/sensors?status=ACTIVE filters properly."""
    response = client.get("/api/sensors?status=ACTIVE")
    assert response.status_code == 200
    data = response.json()
    for s in data:
        assert s["status"] == "ACTIVE"

def test_get_sensor_by_id():
    """Test GET /api/sensors/{sensor_id} retrieves a specific sensor."""
    # List to find first sensor id
    list_res = client.get("/api/sensors")
    sensor_id = list_res.json()[0]["id"]

    response = client.get(f"/api/sensors/{sensor_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sensor_id
    assert "sensor_code" in data
    assert "battery_level" in data

def test_get_sensor_readings():
    """Test GET /api/sensors/{sensor_id}/readings returns time-series readings."""
    list_res = client.get("/api/sensors")
    sensor_id = list_res.json()[0]["id"]

    response = client.get(f"/api/sensors/{sensor_id}/readings?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "sensor_id" in data
    assert "readings" in data
    assert isinstance(data["readings"], list)

def test_get_sensors_health_overview():
    """Test GET /api/sensors/health returns aggregate health diagnostics."""
    response = client.get("/api/sensors/health")
    assert response.status_code == 200
    data = response.json()
    assert "total_sensors" in data
    assert "active_count" in data
    assert "avg_battery" in data
    assert "avg_signal" in data
    assert "sensors" in data
    assert data["total_sensors"] >= 10
    assert len(data["sensors"]) == data["total_sensors"]

def test_ingest_telemetry_reading():
    """Test POST /api/sensors/ingest creates reading records and updates sensor state."""
    list_res = client.get("/api/sensors")
    first_sensor = list_res.json()[0]
    sensor_code = first_sensor["sensor_code"]

    payload = {
        "sensor_code": sensor_code,
        "rainfall_mm": 45.8,
        "water_level_m": 3.42,
        "battery_level": 89.5,
        "signal_strength": -64.2,
        "status": "ACTIVE"
    }

    response = client.post("/api/sensors/ingest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ingested"
    assert data["sensor_code"] == sensor_code
    assert len(data["readings_created"]) > 0

    # Verify sensor state updated
    sensor_res = client.get(f"/api/sensors/{first_sensor['id']}")
    assert sensor_res.json()["battery_level"] == 89.5

def test_websocket_sensors_connection():
    """Test WebSocket connection to /ws/sensors."""
    with client.websocket_connect("/ws/sensors") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_json()
        assert data["event"] == "ack"
        assert data["data"] == "ping"

def test_sensor_simulator_cycle():
    """Test running one simulation cycle programmatically."""
    import sys
    import os
    scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    from scripts.sensor_simulator import SensorSimulator
    import asyncio

    sim = SensorSimulator(interval=1.0)
    sim.init_sensors()
    assert len(sim.states) >= 10

    # Run one step
    asyncio.run(sim.step(force_cloudburst=False))
    assert sim.cycle_count == 1

