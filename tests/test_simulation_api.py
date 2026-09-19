"""Automated integration test suite for POST /api/v1/simulation/run API endpoint."""


def test_run_simulation_api_endpoint(client):
    payload = {
        "rainfall_amount_mm": 200.0,
        "rainfall_duration_hours": 6.0,
        "affected_region": "Riverside & Foothill Region",
        "population_affected": 550,
        "initial_shelter_occupancy": 600,
        "slope_deg": 38.0,
        "elevation_m": 650.0,
    }

    res = client.post("/api/v1/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "simulation_id" in data
    assert "workflow_steps" in data
    assert len(data["workflow_steps"]) == 16
    assert "before_state" in data
    assert "after_state" in data
    assert "alerts" in data
    assert data["after_state"]["hazard_category"] in ["CRITICAL", "HIGH"]
    assert data["after_state"]["affected_population"] == 550
