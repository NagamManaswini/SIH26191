"""Automated unit test suite for Deterministic Disaster Simulation Engine."""

from backend.app.services.simulation_service import run_deterministic_disaster_simulation


def test_deterministic_disaster_simulation_repeatability():
    """Verify that running the simulation with identical parameters produces identical results."""
    res1 = run_deterministic_disaster_simulation(
        rainfall_amount_mm=200.0,
        rainfall_duration_hours=6.0,
        affected_region="Riverside & Foothill Region",
        population_affected=550,
        initial_shelter_occupancy=600,
    )

    res2 = run_deterministic_disaster_simulation(
        rainfall_amount_mm=200.0,
        rainfall_duration_hours=6.0,
        affected_region="Riverside & Foothill Region",
        population_affected=550,
        initial_shelter_occupancy=600,
    )

    assert res1["deterministic_seed"] == res2["deterministic_seed"]
    assert res1["after_state"]["hazard_score"] == res2["after_state"]["hazard_score"]
    assert res1["after_state"]["hazard_category"] == res2["after_state"]["hazard_category"]
    assert res1["after_state"]["affected_population"] == res2["after_state"]["affected_population"]
    assert res1["after_state"]["total_evacuated"] == res2["after_state"]["total_evacuated"]
    assert len(res1["workflow_steps"]) == 16
    assert len(res2["workflow_steps"]) == 16


def test_simulation_workflow_16_steps():
    """Verify that all 16 expected workflow steps are executed with detailed metrics."""
    res = run_deterministic_disaster_simulation(
        rainfall_amount_mm=200.0,
        rainfall_duration_hours=6.0,
    )

    steps = res["workflow_steps"]
    assert len(steps) == 16

    expected_names = [
        "Rainfall Event Update",
        "RISK ANALYSIS",
        "RED ZONES Delineation",
        "AFFECTED POPULATION Identification",
        "ANIMAL POPULATION Identification",
        "HUMAN SHELTER CAPACITY Recalculation",
        "ANIMAL SHELTER CAPACITY Recalculation",
        "SAFE ROUTES Calculation",
        "HUMAN RELOCATION PLAN Generation",
        "ANIMAL RESCUE PLAN Generation",
        "ALERTS Emission",
        "EMERGENCY SOS SOUND Trigger",
        "COMMUNITY BROADCAST Dispatch",
        "AI ASSISTANT Context Refresh",
        "SIMULATION EVENT Storage",
        "COMMAND CENTER DASHBOARD Update",
    ]

    for idx, expected in enumerate(expected_names, 1):
        step = next(s for s in steps if s["step_number"] == idx)
        assert expected in step["step_name"]
        assert step["status"] == "COMPLETED"
        assert "details" in step

