"""Deterministic Multi-Objective Relocation Optimization Engine for SIH26191.

Mathematical Optimization Formulation:
----------------------------------------
Objectives:
1. Maximize evacuation safety & shelter resources.
2. Minimize route travel distance and hazard risk.
3. Prioritize high-vulnerability populations (elderly, children, medical priority).
4. Strictly enforce shelter carrying capacity limits.

Suitability Function S(i, j):
S(i, j) = w_v * VulnerabilityRatio_i + w_s * Safety_j + w_r * Resource_j - w_d * (Distance_ij / MaxDist) - w_rk * RouteRisk_ij

Subject to Constraints:
1. sum_i(x_ij) <= AvailableCapacity_j  forall shelters j (Hard Constraint)
2. sum_j(x_ij) <= TotalPopulation_i    forall groups i   (Hard Constraint)
3. x_ij >= 0                           integer evacuee allocation
"""

from typing import List, Dict, Any, Optional
import math
from shapely.geometry import shape

from gis.routing.graph_builder import haversine_distance_meters
from gis.routing.dijkstra_engine import calculate_safe_evacuation_route


def calculate_group_vulnerability_score(total_pop: int, vuln_pop: int) -> float:
    """Calculate vulnerability ratio (0.0 to 1.0) of a population group."""
    if total_pop <= 0:
        return 0.0
    ratio = vuln_pop / float(total_pop)
    return round(min(1.0, max(0.0, ratio)), 4)


def optimize_relocation_plan(
    population_groups: List[Dict[str, Any]],
    shelters: List[Dict[str, Any]],
    road_graph: Optional[Any] = None,
    risk_preference: str = "strict_safety",
    max_distance_km: float = 50.0,
) -> Dict[str, Any]:
    """Execute deterministic multi-objective relocation assignment algorithm.

    Returns:
      - assignments: List of assigned relocation records with route, distance, risk, and human-readable explanation.
      - unassigned_populations: List of unassigned group records if shelter capacity is exhausted.
      - optimization_summary: Operational metrics (feasibility status, total assigned, total unassigned).
    """
    if not population_groups:
        return {
            "status": "OPTIMAL",
            "message": "No population groups provided for relocation.",
            "assignments": [],
            "unassigned_populations": [],
            "total_evacuated": 0,
            "total_unassigned": 0,
            "optimization_summary": {"feasibility": "OPTIMAL", "satisfaction_score": 1.0},
        }

    # Clone shelter capacity state to track dynamic allocation
    shelter_state: Dict[int, Dict[str, Any]] = {}
    for s in shelters:
        s_id = int(s["id"])
        max_cap = int(s.get("capacity", s.get("maximum_capacity", 100)))
        curr_occ = int(s.get("current_occupancy", 0))
        avail_cap = max(0, max_cap - curr_occ)
        shelter_state[s_id] = {
            "id": s_id,
            "name": str(s.get("name", f"Shelter {s_id}")),
            "max_capacity": max_cap,
            "current_occupancy": curr_occ,
            "available_capacity": avail_cap,
            "accessibility_score": float(s.get("accessibility_score", s.get("accessibility_rating", 0.8))),
            "safety_score": float(s.get("safety_score", s.get("structural_safety_rating", 0.9))),
            "resource_score": float(s.get("resource_score", 0.8)),
            "latitude": float(s.get("latitude", 0.0)),
            "longitude": float(s.get("longitude", 0.0)),
            "status": str(s.get("status", "active")).lower(),
        }

    # Sort population groups by vulnerability score descending (vulnerable populations prioritized first)
    sorted_groups = sorted(
        population_groups,
        key=lambda p: (
            calculate_group_vulnerability_score(p.get("total_population", 1), p.get("vulnerable_population", 0)),
            int(p.get("vulnerable_population", 0)),
        ),
        reverse=True,
    )

    assignments = []
    unassigned_list = []
    total_assigned_count = 0
    total_unassigned_count = 0

    for group in sorted_groups:
        g_id = group.get("id") or group.get("location_name") or "Group"
        g_name = str(group.get("location_name", f"Location {g_id}"))
        g_total = int(group.get("total_population", 0))
        g_vuln = int(group.get("vulnerable_population", 0))
        g_lat = float(group.get("latitude", 0.0))
        g_lon = float(group.get("longitude", 0.0))
        vuln_score = calculate_group_vulnerability_score(g_total, g_vuln)

        remaining_group_pop = g_total

        while remaining_group_pop > 0:
            # Score candidate shelters for remaining population
            candidate_evals = []

            for s_id, s in shelter_state.items():
                if s["available_capacity"] <= 0 or s["status"] != "active":
                    continue

                # Compute Haversine distance
                dist_km = haversine_distance_meters(g_lon, g_lat, s["longitude"], s["latitude"]) / 1000.0
                if dist_km > max_distance_km:
                    continue

                # Compute or estimate route if graph is available
                route_res = None
                if road_graph is not None:
                    route_res = calculate_safe_evacuation_route(
                        G=road_graph,
                        origin_lon=g_lon,
                        origin_lat=g_lat,
                        dest_lon=s["longitude"],
                        dest_lat=s["latitude"],
                        risk_preference=risk_preference,
                    )
                    route_risk = float(route_res.get("route_risk_score", 0.0))
                    r_dist_km = float(route_res.get("total_distance_km", dist_km))
                    is_route_safe = bool(route_res.get("is_safe", True))
                else:
                    route_risk = 0.0
                    r_dist_km = dist_km
                    is_route_safe = True

                # Skip unsafe routes for highly vulnerable groups under strict_safety
                if risk_preference == "strict_safety" and not is_route_safe and vuln_score > 0.3:
                    continue

                # Calculate Suitability Score S(i, j)
                # Weights: Vulnerability (0.25), Safety (0.30), Resources (0.20), Distance (-0.15), Risk (-0.10)
                norm_dist = min(1.0, r_dist_km / max(1.0, max_distance_km))
                suitability = (
                    0.25 * vuln_score
                    + 0.30 * s["safety_score"]
                    + 0.20 * s["resource_score"]
                    - 0.15 * norm_dist
                    - 0.10 * route_risk
                )
                suitability = round(float(suitability), 4)

                candidate_evals.append({
                    "shelter": s,
                    "distance_km": r_dist_km,
                    "route_risk": route_risk,
                    "is_route_safe": is_route_safe,
                    "suitability_score": suitability,
                    "route_res": route_res,
                })

            if not candidate_evals:
                # No feasible shelter available for remaining population
                total_unassigned_count += remaining_group_pop
                unassigned_list.append({
                    "location_name": g_name,
                    "unassigned_population": remaining_group_pop,
                    "vulnerable_count": min(g_vuln, remaining_group_pop),
                    "reason": "Exhausted all active shelter available capacity or no safe evacuation route available.",
                })
                break

            # Sort candidate shelters by suitability_score descending
            candidate_evals.sort(key=lambda c: c["suitability_score"], reverse=True)
            best_candidate = candidate_evals[0]

            selected_shelter = best_candidate["shelter"]
            s_id = selected_shelter["id"]
            avail_cap = selected_shelter["available_capacity"]

            # Allocate evacuees (up to available capacity)
            assigned_count = min(remaining_group_pop, avail_cap)

            # Update shelter state
            selected_shelter["available_capacity"] -= assigned_count
            selected_shelter["current_occupancy"] += assigned_count
            remaining_group_pop -= assigned_count
            total_assigned_count += assigned_count

            # Build GeoJSON route feature
            route_res = best_candidate["route_res"]
            if route_res and route_res.get("route_geometry"):
                route_geom = route_res["route_geometry"]
            else:
                route_geom = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[g_lon, g_lat], [selected_shelter["longitude"], selected_shelter["latitude"]]],
                    },
                    "properties": {"distance_km": best_candidate["distance_km"], "is_safe": best_candidate["is_route_safe"]},
                }

            reason = (
                f"Assigned {assigned_count} evacuees from '{g_name}' to '{selected_shelter['name']}' "
                f"({best_candidate['distance_km']:.1f} km). Selected for safety score {selected_shelter['safety_score']*100:.0f}%, "
                f"resource rating {selected_shelter['resource_score']*100:.0f}%, and low route risk ({best_candidate['route_risk']:.2f}), "
                f"prioritizing {min(g_vuln, assigned_count)} vulnerable individuals."
            )

            assignments.append({
                "source_location_name": g_name,
                "assigned_population_count": assigned_count,
                "vulnerable_assigned_count": min(g_vuln, assigned_count),
                "assigned_shelter_id": s_id,
                "assigned_shelter_name": selected_shelter["name"],
                "distance_km": round(best_candidate["distance_km"], 2),
                "route_risk_score": round(best_candidate["route_risk"], 4),
                "shelter_safety_score": round(selected_shelter["safety_score"], 4),
                "shelter_resource_score": round(selected_shelter["resource_score"], 4),
                "suitability_score": best_candidate["suitability_score"],
                "route_geometry": route_geom,
                "reason_for_assignment": reason,
            })

    # Optimization Status & Summary
    if total_unassigned_count == 0:
        feasibility = "OPTIMAL"
        msg = f"Optimal relocation plan generated: All {total_assigned_count} evacuees assigned to safe shelters."
    elif total_assigned_count > 0:
        feasibility = "FEASIBLE_PARTIAL"
        msg = f"Partial feasible plan generated: {total_assigned_count} evacuees assigned, {total_unassigned_count} unassigned due to capacity limits."
    else:
        feasibility = "INFEASIBLE_FULL_CAPACITY"
        msg = "Infeasible plan: No evacuees could be assigned due to full shelter capacity or inaccessible routes."

    return {
        "status": feasibility,
        "message": msg,
        "assignments": assignments,
        "unassigned_populations": unassigned_list,
        "total_evacuated": total_assigned_count,
        "total_unassigned": total_unassigned_count,
        "optimization_summary": {
            "feasibility": feasibility,
            "total_assigned": total_assigned_count,
            "total_unassigned": total_unassigned_count,
            "shelters_utilized": len(set(a["assigned_shelter_id"] for a in assignments)),
        },
    }
