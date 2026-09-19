"""Road network graph builder for NetworkX with spatial hazard risk calculation."""

from typing import Dict, Any, List, Tuple, Optional
import math
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, shape

from gis.utils.geo_format import sanitize_geometry


def haversine_distance_meters(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculate distance in meters between two lat/lon coordinates."""
    R = 6371000.0  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return float(R * c)


def compute_road_hazard_risk(road_geom: LineString, hazard_zones: List[Dict[str, Any]]) -> float:
    """Calculate spatial hazard risk score (0.0 to 1.0) for a road LineString by spatial intersection."""
    if not hazard_zones or road_geom is None or not road_geom.is_valid:
        return 0.0

    max_risk = 0.0
    for hz in hazard_zones:
        h_geom = hz.get("geometry")
        if h_geom is None:
            continue
        try:
            if not isinstance(h_geom, (Polygon, shape)):
                h_geom = shape(h_geom)
            
            if h_geom.is_valid and road_geom.intersects(h_geom):
                r_score = float(hz.get("risk_score", 0.8))
                r_level = str(hz.get("risk_level", "RED")).upper()
                if r_level in ["CRITICAL", "RED"]:
                    r_score = max(r_score, 0.95)
                elif r_level == "YELLOW":
                    r_score = max(r_score, 0.50)
                max_risk = max(max_risk, r_score)
        except Exception:
            continue

    return round(float(max_risk), 4)


def build_road_network_graph(
    roads_list: List[Dict[str, Any]],
    hazard_zones: Optional[List[Dict[str, Any]]] = None
) -> nx.Graph:
    """Construct a NetworkX Graph representing the road network with spatial hazard risk attributes."""
    G = nx.Graph()
    hazards = hazard_zones or []

    for r_idx, r in enumerate(roads_list):
        path_coords = r.get("path_coords") or r.get("coordinates")
        if not path_coords or len(path_coords) < 2:
            continue

        road_name = r.get("name", f"Road Segment {r_idx+1}")
        road_type = r.get("road_type", "primary")
        condition = str(r.get("condition", "good")).lower()
        passable = bool(r.get("passable", True))

        # Accessibility score from condition
        access_map = {"good": 1.0, "fair": 0.8, "damaged": 0.4, "flooded": 0.1, "blocked": 0.0}
        accessibility = access_map.get(condition, 1.0)
        if not passable or condition == "blocked":
            accessibility = 0.0
            passable = False

        # Build edge segments between consecutive waypoints
        for i in range(len(path_coords) - 1):
            p1 = path_coords[i]
            p2 = path_coords[i + 1]

            node1 = (round(float(p1[0]), 5), round(float(p1[1]), 5))
            node2 = (round(float(p2[0]), 5), round(float(p2[1]), 5))

            dist_m = haversine_distance_meters(node1[1], node1[0], node2[1], node2[0])
            segment_geom = LineString([[node1[0], node1[1]], [node2[0], node2[1]]])

            h_risk = compute_road_hazard_risk(segment_geom, hazards)

            G.add_node(node1, pos=(node1[0], node1[1]))
            G.add_node(node2, pos=(node2[0], node2[1]))

            G.add_edge(
                node1,
                node2,
                name=road_name,
                road_type=road_type,
                condition=condition,
                passable=passable,
                distance_m=dist_m,
                hazard_risk=h_risk,
                accessibility=accessibility,
                geometry=segment_geom,
            )

    return G
