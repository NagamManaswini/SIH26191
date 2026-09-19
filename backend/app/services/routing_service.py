"""Service layer for Safe Evacuation Route calculation."""

import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from shapely.wkt import loads as wkt_loads
from shapely.geometry import mapping, shape

from backend.app.models.entities import Road, HazardZone, Shelter
from backend.app.schemas.route import RouteCalculationRequest, RouteCalculationResponse
from backend.app.utils.geo import point_wkt_to_coords
from gis.routing.graph_builder import build_road_network_graph
from gis.routing.dijkstra_engine import calculate_safe_evacuation_route
from gis.processors.spatial_validator import validate_coordinates


def calculate_evacuation_route_service(
    req: RouteCalculationRequest, db: Session
) -> RouteCalculationResponse:
    """Calculate safe evacuation route using NetworkX & Dijkstra avoiding active Red hazard zones."""
    # 1. Validate Origin Coordinates
    if not validate_coordinates(req.origin.longitude, req.origin.latitude):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid origin coordinates: lon={req.origin.longitude}, lat={req.origin.latitude}",
        )

    # 2. Determine Destination Coordinates
    dest_lat = None
    dest_lon = None

    if req.destination_shelter_id is not None:
        shelter = db.query(Shelter).filter(Shelter.id == req.destination_shelter_id).first()
        if not shelter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination shelter with id {req.destination_shelter_id} not found.",
            )
        s_coords = point_wkt_to_coords(shelter.location)
        if not s_coords:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Destination shelter with id {req.destination_shelter_id} has invalid location coordinates.",
            )
        dest_lon, dest_lat = s_coords[0], s_coords[1]
    elif req.destination is not None:
        if not validate_coordinates(req.destination.longitude, req.destination.latitude):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid destination coordinates: lon={req.destination.longitude}, lat={req.destination.latitude}",
            )
        dest_lon, dest_lat = req.destination.longitude, req.destination.latitude
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either destination coordinates or destination_shelter_id.",
        )

    # 3. Fetch Roads from Database or fallback to Demo Data GeoJSON
    roads_data = []
    db_roads = db.query(Road).all()
    if db_roads:
        for r in db_roads:
            try:
                line_geom = wkt_loads(str(r.path))
                coords = list(line_geom.coords)
                roads_data.append({
                    "name": r.name,
                    "road_type": r.road_type,
                    "condition": r.condition,
                    "passable": r.passable,
                    "path_coords": coords,
                })
            except Exception:
                continue

    if not roads_data:
        demo_roads_path = os.path.join("data", "demo", "roads_network.geojson")
        if os.path.exists(demo_roads_path):
            with open(demo_roads_path, "r") as f:
                geo_data = json.load(f)
                for feat in geo_data.get("features", []):
                    props = feat.get("properties", {})
                    geom = feat.get("geometry", {})
                    coords = geom.get("coordinates", [])
                    if coords and len(coords) >= 2:
                        roads_data.append({
                            "name": props.get("name", "Demo Road"),
                            "road_type": props.get("road_type", "primary"),
                            "condition": props.get("condition", "good"),
                            "passable": True,
                            "path_coords": coords,
                        })

    # 4. Fetch Hazard Zones from Database or fallback to Demo Data
    hazards_data = []
    db_hazards = db.query(HazardZone).all()
    if db_hazards:
        for h in db_hazards:
            try:
                poly_geom = wkt_loads(str(h.boundary))
                hazards_data.append({
                    "name": h.name,
                    "risk_level": h.risk_level,
                    "risk_score": h.risk_score,
                    "geometry": poly_geom,
                })
            except Exception:
                continue

    if not hazards_data:
        demo_hazards_path = os.path.join("data", "demo", "historical_disasters.geojson")
        if os.path.exists(demo_hazards_path):
            with open(demo_hazards_path, "r") as f:
                geo_haz = json.load(f)
                for feat in geo_haz.get("features", []):
                    props = feat.get("properties", {})
                    geom_dict = feat.get("geometry", {})
                    try:
                        hazards_data.append({
                            "name": props.get("title", "Demo Hazard"),
                            "risk_level": props.get("severity", "RED"),
                            "risk_score": 0.90 if props.get("severity") == "CRITICAL" else 0.70,
                            "geometry": shape(geom_dict),
                        })
                    except Exception:
                        continue

    # 5. Build NetworkX Road Graph
    G = build_road_network_graph(roads_list=roads_data, hazard_zones=hazards_data)

    # 6. Calculate Route using Dijkstra Engine
    res = calculate_safe_evacuation_route(
        G=G,
        origin_lon=req.origin.longitude,
        origin_lat=req.origin.latitude,
        dest_lon=dest_lon,
        dest_lat=dest_lat,
        risk_preference=req.risk_preference,
    )

    return RouteCalculationResponse(
        is_safe=res["is_safe"],
        safety_category=res["safety_category"],
        message=res["message"],
        total_distance_km=res["total_distance_km"],
        estimated_travel_time_mins=res["estimated_travel_time_mins"],
        estimated_travel_cost=res["estimated_travel_cost"],
        route_risk_score=res["route_risk_score"],
        route_geometry=res["route_geometry"],
        waypoints=res["waypoints"],
    )
