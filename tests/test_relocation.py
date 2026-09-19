"""Automated test suite for Phase 6 Intelligent Relocation Engine."""

from relocation.optimizer import optimize_relocation_plan, calculate_group_vulnerability_score


def test_vulnerability_score_calculation():
    """Verify group vulnerability score calculation."""
    assert calculate_group_vulnerability_score(100, 40) == 0.4
    assert calculate_group_vulnerability_score(100, 0) == 0.0
    assert calculate_group_vulnerability_score(0, 0) == 0.0


def test_relocation_capacity_limit_enforcement():
    """Verify that relocation engine strictly respects shelter capacity limits and never over-allocates."""
    population_groups = [
        {
            "id": 1,
            "location_name": "Danger Zone Alpha",
            "total_population": 300,
            "vulnerable_population": 50,
            "latitude": 19.0600,
            "longitude": 72.8600,
        }
    ]

    shelters = [
        {
            "id": 101,
            "name": "Small Shelter",
            "capacity": 100,
            "current_occupancy": 0,  # Available: 100
            "safety_score": 0.95,
            "resource_score": 0.90,
            "latitude": 19.0700,
            "longitude": 72.8700,
            "status": "active",
        }
    ]

    plan = optimize_relocation_plan(
        population_groups=population_groups,
        shelters=shelters,
        max_distance_km=50.0,
    )

    assert plan["status"] == "FEASIBLE_PARTIAL"
    assert plan["total_evacuated"] == 100  # Exactly matches available capacity of 100
    assert plan["total_unassigned"] == 200  # 200 unassigned
    assert len(plan["assignments"]) == 1
    assert plan["assignments"][0]["assigned_population_count"] == 100


def test_vulnerable_population_priority_allocation():
    """Verify that higher vulnerability population groups are prioritized for optimal shelters."""
    population_groups = [
        {
            "id": 1,
            "location_name": "Low Vulnerability Group",
            "total_population": 100,
            "vulnerable_population": 5,   # 5%
            "latitude": 19.0600,
            "longitude": 72.8600,
        },
        {
            "id": 2,
            "location_name": "High Vulnerability Hospital Evacuees",
            "total_population": 100,
            "vulnerable_population": 90,  # 90%
            "latitude": 19.0650,
            "longitude": 72.8650,
        },
    ]

    # Two shelters: High safety vs Moderate safety
    shelters = [
        {
            "id": 101,
            "name": "High Safety Shelter",
            "capacity": 100,
            "current_occupancy": 0,  # Available: 100
            "safety_score": 0.98,
            "resource_score": 0.95,
            "latitude": 19.0700,
            "longitude": 72.8700,
            "status": "active",
        },
        {
            "id": 102,
            "name": "Moderate Safety Shelter",
            "capacity": 200,
            "current_occupancy": 0,  # Available: 200
            "safety_score": 0.70,
            "resource_score": 0.70,
            "latitude": 19.0750,
            "longitude": 72.8750,
            "status": "active",
        },
    ]

    plan = optimize_relocation_plan(
        population_groups=population_groups,
        shelters=shelters,
        max_distance_km=50.0,
    )

    assert plan["status"] == "OPTIMAL"
    assert plan["total_evacuated"] == 200

    # High Vulnerability group MUST be assigned to High Safety Shelter (id 101)
    high_vuln_assignment = next(
        a for a in plan["assignments"] if "High Vulnerability" in a["source_location_name"]
    )
    assert high_vuln_assignment["assigned_shelter_id"] == 101
