"""Automated test suite for Safe Evacuation Routing API POST /api/v1/routes/calculate."""


def test_calculate_route_valid_destination_coords(client):
    payload = {
        "origin": {"latitude": 19.0600, "longitude": 72.8600},
        "destination": {"latitude": 19.1400, "longitude": 72.9400},
        "risk_preference": "balanced",
    }

    res = client.post("/api/v1/routes/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "is_safe" in data
    assert "safety_category" in data
    assert "total_distance_km" in data
    assert "route_geometry" in data
    assert data["route_geometry"]["type"] == "Feature"
    assert "type" in data["route_geometry"]["geometry"]


def test_calculate_route_valid_destination_shelter_id(client):
    # 1. Create a shelter first
    shelter_payload = {
        "name": "Evacuation Destination Shelter",
        "capacity": 500,
        "latitude": 19.1300,
        "longitude": 72.9200,
    }
    s_res = client.post("/api/v1/shelters", json=shelter_payload)
    shelter_id = s_res.json()["id"]

    # 2. Calculate route to shelter ID
    route_payload = {
        "origin": {"latitude": 19.0700, "longitude": 72.8700},
        "destination_shelter_id": shelter_id,
        "risk_preference": "balanced",
    }

    res = client.post("/api/v1/routes/calculate", json=route_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_distance_km"] >= 0.0


def test_calculate_route_invalid_coordinates_bad_request(client):
    invalid_payload = {
        "origin": {"latitude": 195.0, "longitude": 72.8600},  # Invalid lat > 90
        "destination": {"latitude": 19.1400, "longitude": 72.9400},
    }

    res = client.post("/api/v1/routes/calculate", json=invalid_payload)
    assert res.status_code == 422  # Pydantic validation catches lat <= 90.0 constraint
