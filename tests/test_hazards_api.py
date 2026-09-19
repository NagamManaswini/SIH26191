"""Automated test suite for Phase 2 Hazard API endpoints."""

import pytest


def test_create_and_get_hazard(client):
    payload = {
        "name": "Northern Slope Landslide Threat",
        "hazard_type": "landslide",
        "risk_level": "HIGH",
        "risk_score": 0.78,
        "coordinates": [
            [
                [72.90, 19.10],
                [72.92, 19.10],
                [72.92, 19.12],
                [72.90, 19.12],
                [72.90, 19.10],
            ]
        ],
    }

    # Create
    res = client.post("/api/v1/hazards", json=payload)
    assert res.status_code == 201
    data = res.json()
    hazard_id = data["id"]
    assert data["name"] == payload["name"]
    assert data["risk_level"] == "HIGH"

    # Get by ID
    get_res = client.get(f"/api/v1/hazards/{hazard_id}")
    assert get_res.status_code == 200
    assert get_res.json()["risk_score"] == 0.78

    # List hazards
    list_res = client.get("/api/v1/hazards")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_hazards_map_geojson_endpoint(client):
    # Ensure at least one hazard exists
    payload = {
        "name": "Flood Plain GeoJSON Test",
        "hazard_type": "flood",
        "risk_level": "CRITICAL",
        "risk_score": 0.95,
        "coordinates": [
            [
                [72.85, 19.05],
                [72.88, 19.05],
                [72.88, 19.08],
                [72.85, 19.08],
                [72.85, 19.05],
            ]
        ],
    }
    client.post("/api/v1/hazards", json=payload)

    # GET /api/v1/hazards/map
    res = client.get("/api/v1/hazards/map")
    assert res.status_code == 200
    geojson = res.json()

    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    assert isinstance(geojson["features"], list)
    assert len(geojson["features"]) >= 1

    feature = geojson["features"][0]
    assert feature["type"] == "Feature"
    assert "geometry" in feature
    assert feature["geometry"]["type"] == "Polygon"
    assert "properties" in feature
    assert "risk_level" in feature["properties"]


def test_hazards_analyze_endpoint(client):
    req_payload = {
        "rainfall_mm": 220.0,
        "region_name": "Test Catchment Sector",
        "weight_rainfall": 0.40,
        "weight_slope": 0.35,
        "threshold_low": 0.25,
        "threshold_moderate": 0.50,
        "threshold_high": 0.75,
    }

    res = client.post("/api/v1/hazards/analyze", json=req_payload)
    assert res.status_code == 200
    analyzed_hazards = res.json()
    assert isinstance(analyzed_hazards, list)

    # Verify hazards were persisted in DB
    list_res = client.get("/api/v1/hazards")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= len(analyzed_hazards)
