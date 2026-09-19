"""Full End-to-End Disaster Simulation Integration Test.

Runs 200 mm rainfall in 6 hours and verifies complete 16-step disaster workflow:
Risk -> Red Zone -> Humans & Animals -> Shelters -> Safe Dijkstra Detour -> SOS Sound Alert -> Broadcast -> AI Assistant Context.
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_200mm_rainfall_disaster_simulation_integration():
    """Verify 200mm rainfall scenario executes all 16 workflow steps successfully."""
    response = client.post(
        "/api/v1/simulation/run",
        json={
            "rainfall_amount_mm": 200.0,
            "rainfall_duration_hours": 6.0,
            "affected_region": "Riverside & Foothill Region",
            "population_affected": 550,
            "initial_shelter_occupancy": 600,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["parameters"]["rainfall_amount_mm"] == 200.0
    assert data["after_state"]["hazard_category"] in ["CRITICAL", "HIGH"]
    assert data["after_state"]["red_zones_count"] == 2
    assert data["after_state"]["affected_population"] == 550
    assert data["after_state"]["at_risk_animals"] == 120
    assert data["after_state"]["sos_sound_triggered"] is True

    # Verify 16 workflow steps returned
    steps = data["workflow_steps"]
    assert len(steps) == 16

    step_names = [s["step_name"] for s in steps]
    assert "Rainfall Event Update" in step_names[0]
    assert "RISK ANALYSIS" in step_names[1]
    assert "ANIMAL POPULATION Identification" in step_names[4]
    assert "EMERGENCY SOS SOUND Trigger" in step_names[11]
    assert "COMMUNITY BROADCAST Dispatch" in step_names[12]
    assert "AI ASSISTANT Context Refresh" in step_names[13]
