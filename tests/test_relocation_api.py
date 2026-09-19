"""Automated integration test suite for Relocation API POST /api/v1/relocation/plan."""


def test_relocation_plan_api_endpoint(client):
    payload = {
        "population_groups": [
            {
                "location_name": "Red Zone Alpha - Riverside",
                "total_population": 150,
                "vulnerable_population": 45,
                "latitude": 19.0600,
                "longitude": 72.8600,
            },
            {
                "location_name": "Red Zone Beta - Hillside",
                "total_population": 200,
                "vulnerable_population": 30,
                "latitude": 19.1100,
                "longitude": 72.9100,
            },
        ],
        "risk_preference": "strict_safety",
        "max_distance_km": 50.0,
    }

    res = client.post("/api/v1/relocation/plan", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "status" in data
    assert data["status"] in ["OPTIMAL", "FEASIBLE_PARTIAL", "INFEASIBLE_FULL_CAPACITY"]
    assert "assignments" in data
    assert isinstance(data["assignments"], list)
    assert "total_evacuated" in data
    assert "optimization_summary" in data

    if data["assignments"]:
        first_assign = data["assignments"][0]
        assert "source_location_name" in first_assign
        assert "assigned_shelter_name" in first_assign
        assert "reason_for_assignment" in first_assign
        assert "route_geometry" in first_assign
