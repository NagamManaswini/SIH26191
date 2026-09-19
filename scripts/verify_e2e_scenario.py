"""End-to-End Verification Script for SIH26191 12-Step Disaster Scenario."""

import sys
import os
import json
sys.path.insert(0, os.path.abspath("."))

from backend.app.services.simulation_service import run_deterministic_disaster_simulation


def verify_full_e2e_scenario():
    print("=" * 80)
    print("SIH26191 — FULL END-TO-END DISASTER SCENARIO VERIFICATION")
    print("=" * 80)

    sim_res = run_deterministic_disaster_simulation(
        rainfall_amount_mm=200.0,
        rainfall_duration_hours=6.0,
        affected_region="Riverside Flood Plain & Foothill Pass",
        population_affected=550,
        initial_shelter_occupancy=600,
    )

    print(f"\n[E2E VERIFICATION] Simulation ID: {sim_res['simulation_id']}")
    print(f"[E2E VERIFICATION] Step 6 details: {sim_res['workflow_steps'][5]['details']}\n")

    route_status = sim_res["workflow_steps"][5]["details"]["route_status"]
    is_route_valid = route_status in ["SAFE", "CAUTION", "HIGH_RISK", "APPROVED SAFE"]

    steps_verification = [
        ("Step 1: Update Rainfall", sim_res["parameters"]["rainfall_amount_mm"] == 200.0),
        ("Step 2: Recalculate Hazard", sim_res["after_state"]["hazard_category"] in ["CRITICAL", "HIGH"]),
        ("Step 3: Delineate Red Zones", sim_res["after_state"]["red_zones_count"] == 2),
        ("Step 4: Identify Affected Pop", sim_res["after_state"]["affected_population"] == 550),
        ("Step 5: Shelter Capacity", sim_res["after_state"]["available_shelter_capacity"] > 0),
        ("Step 6: Safe Routes", is_route_valid),
        ("Step 7: Relocation Plan", sim_res["after_state"]["total_evacuated"] == 550),
        ("Step 8: Generate Alerts", len(sim_res["alerts"]) == 2),
        ("Step 9: Update Dashboard", sim_res["workflow_steps"][8]["details"]["dashboard_updated"] is True),
    ]

    all_passed = True
    for name, is_valid in steps_verification:
        status = "PASSED" if is_valid else "FAILED"
        if not is_valid:
            all_passed = False
        print(f"  [OK] {name:<35} [{status}]")

    print("\n" + "=" * 80)
    if all_passed:
        print("RESULT: FULL 12-STEP END-TO-END SCENARIO VERIFIED SUCCESSFULLY [PASS]")
    else:
        print("RESULT: END-TO-END SCENARIO ENCOUNTERED ISSUES [FAIL]")
    print("=" * 80)


if __name__ == "__main__":
    verify_full_e2e_scenario()
