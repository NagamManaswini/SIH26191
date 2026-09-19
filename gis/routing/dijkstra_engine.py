"""Hazard-aware Dijkstra safe evacuation routing engine using NetworkX."""

from typing import Dict, Any, List, Tuple, Optional
import math
import networkx as nx
from shapely.geometry import LineString, mapping

from gis.routing.graph_builder import haversine_distance_meters, build_road_network_graph


def find_nearest_node(G: nx.Graph, lon: float, lat: float) -> Optional[Tuple[float, float]]:
    """Find the nearest graph node to a given (lon, lat) coordinate."""
    if not G or len(G.nodes) == 0:
        return None

    best_node = None
    min_dist = float("inf")

    for node in G.nodes:
        n_lon, n_lat = node
        dist = haversine_distance_meters(lon, lat, n_lon, n_lat)
        if dist < min_dist:
            min_dist = dist
            best_node = node

    return best_node


def calculate_safe_evacuation_route(
    G: nx.Graph,
    origin_lon: float,
    origin_lat: float,
    dest_lon: float,
    dest_lat: float,
    risk_preference: str = "strict_safety",
) -> Dict[str, Any]:
    """Compute hazard-aware safe evacuation route using Dijkstra's algorithm.

    Algorithm Rationale:
    --------------------
    1. Risk Preferences:
       - 'strict_safety': Excludes edges intersecting CRITICAL/RED hazard zones (risk >= 0.75) or blocked roads.
       - 'balanced': Heavily penalizes high-risk edges with quadratic cost multiplier (1.0 + 8.0 * risk^2).
       - 'shortest_distance': Minimally penalizes risk, prioritizing shortest geographic path.
    2. Shortest Geographical Route Avoidance:
       The cost function inflates edge weight exponentially based on hazard_risk. If a direct short path passes
       through a Red Zone, Dijkstra automatically selects a safer detour around the hazard zone.
    3. Failure Handling:
       If all paths are cut off by hazard zones or blocked roads, returns 'NO_SAFE_ROUTE'.
    """
    pref = str(risk_preference).strip().lower()
    if pref not in ["strict_safety", "balanced", "shortest_distance"]:
        pref = "strict_safety"

    empty_response = {
        "is_safe": False,
        "safety_category": "NO_SAFE_ROUTE",
        "message": "No safe evacuation route available.",
        "total_distance_km": 0.0,
        "estimated_travel_time_mins": 0.0,
        "estimated_travel_cost": 0.0,
        "route_risk_score": 1.0,
        "route_geometry": {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": []},
            "properties": {"is_safe": False, "safety_category": "NO_SAFE_ROUTE"},
        },
        "waypoints": [],
    }

    if not G or len(G.nodes) < 2:
        empty_response["message"] = "No safe evacuation route available. Road network graph is empty or disconnected."
        return empty_response

    # Find nearest nodes
    source_node = find_nearest_node(G, origin_lon, origin_lat)
    target_node = find_nearest_node(G, dest_lon, dest_lat)

    if not source_node or not target_node or source_node == target_node:
        empty_response["message"] = "No safe evacuation route available. Origin or destination is too far from known road network."
        return empty_response

    # Weight function
    def edge_weight_fn(u, v, d):
        dist_m = float(d.get("distance_m", 1.0))
        h_risk = float(d.get("hazard_risk", 0.0))
        passable = bool(d.get("passable", True))
        accessibility = float(d.get("accessibility", 1.0))

        if not passable or accessibility <= 0.0:
            return float("inf")

        if pref == "strict_safety":
            if h_risk >= 0.75:  # Block RED / CRITICAL hazard zones in strict safety mode
                return float("inf")
            cost_mult = 1.0 + 15.0 * (h_risk ** 2)
        elif pref == "balanced":
            if h_risk >= 0.95:
                return float("inf")
            cost_mult = 1.0 + 6.0 * (h_risk ** 2)
        else:  # shortest_distance
            cost_mult = 1.0 + 0.5 * h_risk

        return (dist_m * cost_mult) / max(0.2, accessibility)

    try:
        path_nodes = nx.dijkstra_path(G, source_node, target_node, weight=edge_weight_fn)
    except Exception:
        path_nodes = []

    if not path_nodes:
        empty_response["message"] = "No safe evacuation route available. All candidate roads are blocked or cut off by critical hazard zones."
        return empty_response

    waypoints = [list(n) for n in path_nodes]

    if len(waypoints) < 2:
        empty_response["message"] = "No safe evacuation route available. Route path contains insufficient points."
        return empty_response

    # Aggregate route metrics & check for infinite cost/impassable segments
    total_dist_m = 0.0
    total_cost = 0.0
    max_edge_risk = 0.0
    sum_weighted_risk = 0.0
    has_impassable_segment = False

    for i in range(len(path_nodes) - 1):
        u, v = path_nodes[i], path_nodes[i + 1]
        edge_data = G[u][v]
        d_m = float(edge_data.get("distance_m", 0.0))
        r_risk = float(edge_data.get("hazard_risk", 0.0))
        passable = bool(edge_data.get("passable", True))
        access = float(edge_data.get("accessibility", 1.0))
        e_cost = edge_weight_fn(u, v, edge_data)

        if e_cost == float("inf") or not passable or access <= 0.0:
            has_impassable_segment = True

        total_dist_m += d_m
        total_cost += e_cost if e_cost != float("inf") else d_m * 10.0
        max_edge_risk = max(max_edge_risk, r_risk)
        sum_weighted_risk += r_risk * d_m

    if has_impassable_segment:
        empty_response["message"] = "No safe evacuation route available. Path contains blocked or impassable road segments."
        return empty_response

    total_dist_km = round(total_dist_m / 1000.0, 2)
    travel_time_mins = round(total_dist_km * 1.5, 1)  # ~40 km/h average speed
    avg_route_risk = round(sum_weighted_risk / max(1.0, total_dist_m), 4)

    # Determine safety category
    if max_edge_risk >= 0.75 or avg_route_risk >= 0.50:
        safety_cat = "HIGH_RISK"
        is_safe = False
    elif max_edge_risk >= 0.35 or avg_route_risk >= 0.20:
        safety_cat = "CAUTION"
        is_safe = True
    else:
        safety_cat = "SAFE"
        is_safe = True

    route_line = LineString(waypoints)
    geojson_feature = {
        "type": "Feature",
        "geometry": mapping(route_line),
        "properties": {
            "total_distance_km": total_dist_km,
            "estimated_travel_time_mins": travel_time_mins,
            "estimated_travel_cost": round(total_cost, 2),
            "route_risk_score": avg_route_risk,
            "max_hazard_risk": max_edge_risk,
            "safety_category": safety_cat,
            "is_safe": is_safe,
            "risk_preference": pref,
        },
    }

    return {
        "is_safe": is_safe,
        "safety_category": safety_cat,
        "message": f"Successfully calculated evacuation route ({safety_cat}).",
        "total_distance_km": total_dist_km,
        "estimated_travel_time_mins": travel_time_mins,
        "estimated_travel_cost": round(total_cost, 2),
        "route_risk_score": avg_route_risk,
        "route_geometry": geojson_feature,
        "waypoints": waypoints,
    }
