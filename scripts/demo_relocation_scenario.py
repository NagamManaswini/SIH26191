"""Demo Scenario Script for Hackathon Presentation: Intelligent Relocation Optimization.

Demonstrates multi-objective relocation assignment of vulnerable populations from Red Hazard Zones
to emergency shelters without exceeding carrying capacity limits.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import json
from shapely.geometry import Polygon
from gis.routing.graph_builder import build_road_network_graph
from relocation.optimizer import optimize_relocation_plan


def run_demo_relocation_scenario():
    print("=" * 80)
    print("SIH26191 — HACKATHON DEMO: INTELLIGENT RELOCATION OPTIMIZATION SCENARIO")
    print("=" * 80)

    # 1. Population Groups in Danger Zones
    population_groups = [
        {
            "id": 1,
            "location_name": "Red Zone Alpha (Riverside Flood Plain)",
            "total_population": 300,
            "vulnerable_population": 120,  # High vulnerability (40%)
            "latitude": 19.0600,
            "longitude": 72.8600,
        },
        {
            "id": 2,
            "location_name": "Red Zone Beta (Steep Landslide Slope)",
            "total_population": 250,
            "vulnerable_population": 50,   # Moderate vulnerability (20%)
            "latitude": 19.1100,
            "longitude": 72.9100,
        },
    ]

    # 2. Candidate Emergency Shelters
    shelters = [
        {
            "id": 101,
            "name": "Central High School Relief Shelter",
            "capacity": 350,
            "current_occupancy": 100,      # Available: 250
            "safety_score": 0.95,
            "resource_score": 0.90,
            "latitude": 19.0700,
            "longitude": 72.8700,
            "status": "active",
        },
        {
            "id": 102,
            "name": "North Ridge Community Stadium",
            "capacity": 800,
            "current_occupancy": 500,      # Available: 300
            "safety_score": 0.88,
            "resource_score": 0.82,
            "latitude": 19.1300,
            "longitude": 72.9300,
            "status": "active",
        },
    ]

    # 3. Road Network Segments
    roads = [
        {
            "name": "Riverside Highway (Direct)",
            "condition": "good",
            "passable": True,
            "path_coords": [[72.8600, 19.0600], [72.8700, 19.0700]],
        },
        {
            "name": "Expressway Connect",
            "condition": "good",
            "passable": True,
            "path_coords": [[72.8700, 19.0700], [72.9300, 19.1300]],
        },
        {
            "name": "Hill Access Road",
            "condition": "good",
            "passable": True,
            "path_coords": [[72.9100, 19.1100], [72.9300, 19.1300]],
        },
    ]

    hazard_zones = [
        {
            "name": "Landslide Hazard Zone",
            "risk_level": "RED",
            "risk_score": 0.90,
            "geometry": Polygon([[72.89, 19.08], [72.92, 19.08], [72.92, 19.10], [72.89, 19.10], [72.89, 19.08]]),
        }
    ]

    road_graph = build_road_network_graph(roads_list=roads, hazard_zones=hazard_zones)

    # 4. Execute Relocation Engine
    plan = optimize_relocation_plan(
        population_groups=population_groups,
        shelters=shelters,
        road_graph=road_graph,
        risk_preference="strict_safety",
        max_distance_km=40.0,
    )

    # 5. Print Hackathon Judge Summary
    print(f"\nOptimization Status: {plan['status']}")
    print(f"Message: {plan['message']}\n")

    print("ASSIGNMENT SUMMARY:")
    print("-" * 80)
    for idx, a in enumerate(plan["assignments"], 1):
        print(f"[{idx}] {a['source_location_name']} -> {a['assigned_shelter_name']}")
        print(f"    - Assigned Count: {a['assigned_population_count']} people ({a['vulnerable_assigned_count']} vulnerable)")
        print(f"    - Route Distance: {a['distance_km']} km | Route Risk: {a['route_risk_score']}")
        print(f"    - Shelter Safety: {a['shelter_safety_score']*100:.0f}% | Suitability Score: {a['suitability_score']}")
        print(f"    - Transparent Decision Rationale:\n      \"{a['reason_for_assignment']}\"\n")

    if plan["unassigned_populations"]:
        print("UNASSIGNED OVERFLOW (CAPACITY EXHAUSTED):")
        print("-" * 80)
        for u in plan["unassigned_populations"]:
            print(f"  - Location: {u['location_name']} | Count: {u['unassigned_population']} | Reason: {u['reason']}")

    print("=" * 80)
    print("DEMO SCENARIO EXECUTED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    run_demo_relocation_scenario()
