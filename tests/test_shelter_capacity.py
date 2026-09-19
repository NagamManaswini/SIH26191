"""Automated unit and integration test suite for Phase 4 Shelter Carrying Capacity Assessment Engine."""

from backend.app.models.entities import Shelter, ShelterResource
from backend.app.utils.geo import coords_to_point_wkt
from backend.app.services.capacity_engine import compute_resource_score, evaluate_shelter_capacity


def test_capacity_score_calculations(db):
    """Test capacity, resource_score, accessibility_score, safety_score, and overall_suitability calculations."""
    wkt_loc = coords_to_point_wkt(72.87, 19.07)
    shelter = Shelter(
        name="Test High School Shelter",
        address="Central Sector",
        capacity=500,
        current_occupancy=100,
        status="active",
        accessibility_rating=0.85,
        structural_safety_rating=0.95,
        location=wkt_loc,
    )
    db.add(shelter)
    db.commit()
    db.refresh(shelter)

    resources = ShelterResource(
        shelter_id=shelter.id,
        water_supply_days=7.0,
        food_supply_days=7.0,
        medical_kits=50,
        power_backup=True,
        sanitation_facilities=20,
    )
    db.add(resources)
    db.commit()

    metrics = evaluate_shelter_capacity(shelter, db)

    assert metrics.maximum_capacity == 500
    assert metrics.current_occupancy == 100
    assert metrics.available_capacity == 400
    assert metrics.occupancy_percentage == 20.0
    assert metrics.resource_score == 1.0  # Perfect resources score
    assert metrics.accessibility_score == 0.85
    assert metrics.safety_score == 0.95
    assert metrics.can_accept_evacuees is True
    assert metrics.overall_suitability > 0.5


def test_prevent_over_capacity_assignment_validation(client):
    """Test that setting current_occupancy greater than maximum_capacity raises a 400 Bad Request error."""
    payload = {
        "name": "Overcrowded Shelter",
        "capacity": 100,
        "current_occupancy": 150,  # Invalid: > capacity
        "latitude": 19.05,
        "longitude": 72.85,
    }
    res = client.post("/api/v1/shelters", json=payload)
    assert res.status_code == 400
    assert "occupancy cannot exceed" in res.json()["detail"]


def test_get_all_shelter_capacities_endpoint(client):
    """Test GET /api/v1/shelters/capacity endpoint."""
    s1 = {
        "name": "Shelter A",
        "capacity": 300,
        "current_occupancy": 50,
        "latitude": 19.07,
        "longitude": 72.87,
    }
    s2 = {
        "name": "Shelter B",
        "capacity": 200,
        "current_occupancy": 190,
        "latitude": 19.08,
        "longitude": 72.88,
    }
    client.post("/api/v1/shelters", json=s1)
    client.post("/api/v1/shelters", json=s2)

    res = client.get("/api/v1/shelters/capacity")
    assert res.status_code == 200
    capacities = res.json()
    assert isinstance(capacities, list)
    assert len(capacities) >= 2

    # Verify filter min_available_capacity=100 (Shelter B only has 10 available)
    filtered_res = client.get("/api/v1/shelters/capacity?min_available_capacity=100")
    assert filtered_res.status_code == 200
    filtered_data = filtered_res.json()
    assert all(item["available_capacity"] >= 100 for item in filtered_data)


def test_get_shelter_capacity_by_id_endpoint(client):
    """Test GET /api/v1/shelters/{id}/capacity endpoint."""
    payload = {
        "name": "Single Test Shelter",
        "capacity": 400,
        "current_occupancy": 100,
        "latitude": 19.10,
        "longitude": 72.90,
    }
    create_res = client.post("/api/v1/shelters", json=payload)
    shelter_id = create_res.json()["id"]

    res = client.get(f"/api/v1/shelters/{shelter_id}/capacity")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == shelter_id
    assert data["available_capacity"] == 300
    assert "resource_score" in data
    assert "overall_suitability" in data


def test_evaluate_shelter_relocation_assignment_endpoint(client):
    """Test POST /api/v1/shelters/evaluate evacuee assignment engine."""
    s1 = {
        "name": "Small Shelter",
        "capacity": 50,
        "current_occupancy": 10,
        "latitude": 19.07,
        "longitude": 72.87,
    }
    s2 = {
        "name": "Large Shelter",
        "capacity": 500,
        "current_occupancy": 50,
        "latitude": 19.08,
        "longitude": 72.88,
    }
    client.post("/api/v1/shelters", json=s1)
    client.post("/api/v1/shelters", json=s2)

    # Request assignment for 200 evacuees (Small Shelter can't fit, Large Shelter fits)
    eval_req = {
        "evacuee_count": 200,
        "origin_latitude": 19.075,
        "origin_longitude": 72.875,
        "max_distance_km": 30.0,
    }

    res = client.post("/api/v1/shelters/evaluate", json=eval_req)
    assert res.status_code == 200
    eval_data = res.json()

    assert eval_data["is_assignment_possible"] is True
    assert eval_data["assigned_shelter_name"] == "Large Shelter"
    assert len(eval_data["suitable_shelters"]) >= 1

    # Request assignment for 1000 evacuees (Exceeds all shelter available capacities)
    eval_req_too_large = {
        "evacuee_count": 1000,
        "origin_latitude": 19.075,
        "origin_longitude": 72.875,
    }
    res_large = client.post("/api/v1/shelters/evaluate", json=eval_req_too_large)
    assert res_large.status_code == 200
    large_data = res_large.json()

    assert large_data["is_assignment_possible"] is False
    assert large_data["assigned_shelter_id"] is None
    assert "No single shelter has sufficient available capacity" in large_data["message"]
