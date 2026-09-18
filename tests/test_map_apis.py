import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_map_sensors_geojson():
    response = client.get("/api/map/sensors")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert isinstance(data["features"], list)
    
    if len(data["features"]) > 0:
        f = data["features"][0]
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] == "Point"
        assert len(f["geometry"]["coordinates"]) == 2
        props = f["properties"]
        assert "sensor_code" in props
        assert "sensor_type" in props
        assert "status" in props
        assert "battery_level" in props
        assert "signal_strength" in props


def test_get_map_watersheds_geojson():
    response = client.get("/api/map/watersheds")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert len(data["features"]) >= 5
    
    ws_feature = data["features"][0]
    assert ws_feature["type"] == "Feature"
    assert ws_feature["geometry"]["type"] in ("Polygon", "MultiPolygon")
    props = ws_feature["properties"]
    assert "name" in props
    assert "risk_level" in props
    assert "rainfall_avg_mm" in props
    assert "river_level_max_m" in props
    assert "soil_moisture_avg_pct" in props


def test_get_map_risk_zones():
    response = client.get("/api/map/risk-zones")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 3
    
    rz = data["features"][0]
    assert rz["geometry"]["type"] == "Polygon"
    assert "risk_level" in rz["properties"]
    assert "expected_depth_m" in rz["properties"]
    assert "hazard_type" in rz["properties"]


def test_get_map_evacuation_centers():
    response = client.get("/api/map/evacuation-centers")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 5
    
    ec = data["features"][0]
    assert ec["geometry"]["type"] == "Point"
    assert "capacity" in ec["properties"]
    assert "current_occupancy" in ec["properties"]
    assert "occupancy_rate" in ec["properties"]


def test_get_map_citizen_reports():
    response = client.get("/api/map/citizen-reports")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert isinstance(data["features"], list)


def test_get_map_alerts():
    response = client.get("/api/map/alerts")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert isinstance(data["features"], list)
