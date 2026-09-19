"""Automated unit and integration test suite for NetworkX Dijkstra Safe Evacuation Routing Engine."""

from shapely.geometry import Polygon
from gis.routing.graph_builder import build_road_network_graph
from gis.routing.dijkstra_engine import calculate_safe_evacuation_route


def test_shortest_vs_safe_route_avoidance():
    """Verify that the routing engine bypasses a direct high-risk road segment in favor of a safe detour."""
    roads = [
        {
            "name": "Direct High-Risk Highway",
            "condition": "good",
            "passable": True,
            "path_coords": [[72.85, 19.05], [72.95, 19.05]],
        },
        {
            "name": "North Safe Detour Segment 1",
            "condition": "good",
            "passable": True,
            "path_coords": [[72.85, 19.05], [72.90, 19.12]],
        },
        {
            "name": "North Safe Detour Segment 2",
            "condition": "good",
            "passable": True,
            "path_coords": [[72.90, 19.12], [72.95, 19.05]],
        },
    ]

    hazard_zones = [
        {
            "name": "Landslide Red Zone",
            "risk_level": "RED",
            "risk_score": 0.95,
            "geometry": Polygon([[72.88, 19.04], [72.92, 19.04], [72.92, 19.06], [72.88, 19.06], [72.88, 19.04]]),
        }
    ]

    G = build_road_network_graph(roads_list=roads, hazard_zones=hazard_zones)

    route_res = calculate_safe_evacuation_route(
        G=G,
        origin_lon=72.85,
        origin_lat=19.05,
        dest_lon=72.95,
        dest_lat=19.05,
        risk_preference="strict_safety",
    )

    assert route_res["is_safe"] is True
    assert route_res["safety_category"] == "SAFE"
    assert len(route_res["waypoints"]) == 3
    assert route_res["waypoints"][1] == [72.90, 19.12]


def test_no_safe_route_condition():
    """Verify that engine returns NO_SAFE_ROUTE when all candidate roads are impassable or cut off."""
    roads = [
        {
            "name": "Blocked Mountain Pass",
            "condition": "blocked",
            "passable": False,
            "path_coords": [[72.85, 19.05], [72.95, 19.05]],
        }
    ]
    G = build_road_network_graph(roads_list=roads, hazard_zones=[])

    route_res = calculate_safe_evacuation_route(
        G=G,
        origin_lon=72.85,
        origin_lat=19.05,
        dest_lon=72.95,
        dest_lat=19.05,
        risk_preference="strict_safety",
    )

    assert route_res["is_safe"] is False
    assert route_res["safety_category"] == "NO_SAFE_ROUTE"
    assert "No safe evacuation route" in route_res["message"]
