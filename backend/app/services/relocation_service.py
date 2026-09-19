"""Service layer for Intelligent Relocation Optimization."""

import os
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from shapely.wkt import loads as wkt_loads
from shapely.geometry import shape

from backend.app.models.entities import Shelter, Population, Road, HazardZone
from backend.app.schemas.relocation import RelocationPlanRequest, RelocationPlanResponse
from backend.app.services.capacity_engine import evaluate_shelter_capacity
from backend.app.utils.geo import point_wkt_to_coords, polygon_wkt_to_centroid
from gis.routing.graph_builder import build_road_network_graph
from relocation.optimizer import optimize_relocation_plan


def generate_relocation_plan_service(
    req: RelocationPlanRequest, db: Session
) -> RelocationPlanResponse:
    """Service to execute relocation planning optimization across shelters and road graph."""
    # 1. Collect Population Groups Input
    pop_groups: List[Dict[str, Any]] = []

    if req.population_groups:
        for p in req.population_groups:
            pop_groups.append({
                "id": p.id or p.location_name,
                "location_name": p.location_name,
                "total_population": p.total_population,
                "vulnerable_population": p.vulnerable_population,
                "latitude": p.latitude,
                "longitude": p.longitude,
            })
    else:
        # Fallback to database population records
        db_pops = db.query(Population).all()
        for p in db_pops:
            centroid = polygon_wkt_to_centroid(p.area_geometry)
            lat = centroid[1] if centroid else 19.0700
            lon = centroid[0] if centroid else 72.8700
            pop_groups.append({
                "id": p.id,
                "location_name": p.location_name,
                "total_population": p.total_population,
                "vulnerable_population": p.vulnerable_population,
                "latitude": lat,
                "longitude": lon,
            })

    # 2. Collect Shelters with Capacity & Suitability metrics
    shelter_dicts: List[Dict[str, Any]] = []
    db_shelters = db.query(Shelter).all()

    if db_shelters:
        for s in db_shelters:
            metrics = evaluate_shelter_capacity(s, db)
            shelter_dicts.append({
                "id": s.id,
                "name": s.name,
                "capacity": s.capacity,
                "current_occupancy": s.current_occupancy,
                "safety_score": metrics.safety_score,
                "resource_score": metrics.resource_score,
                "accessibility_score": metrics.accessibility_score,
                "latitude": metrics.latitude,
                "longitude": metrics.longitude,
                "status": s.status,
            })

    if not shelter_dicts:
        # Seeded demo shelters fallback if DB empty
        shelter_dicts = [
            {
                "id": 1,
                "name": "Central High School Relief Shelter",
                "capacity": 500,
                "current_occupancy": 120,
                "safety_score": 0.95,
                "resource_score": 0.90,
                "accessibility_score": 0.90,
                "latitude": 19.07,
                "longitude": 72.87,
                "status": "active",
            },
            {
                "id": 2,
                "name": "North Ridge Community Stadium",
                "capacity": 1200,
                "current_occupancy": 850,
                "safety_score": 0.90,
                "resource_score": 0.85,
                "accessibility_score": 0.85,
                "latitude": 19.13,
                "longitude": 72.92,
                "status": "active",
            },
        ]

    # 3. Build Road Graph
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

    road_graph = build_road_network_graph(roads_list=roads_data, hazard_zones=hazards_data)

    # 4. Execute Relocation Optimization Engine
    opt_result = optimize_relocation_plan(
        population_groups=pop_groups,
        shelters=shelter_dicts,
        road_graph=road_graph,
        risk_preference=req.risk_preference,
        max_distance_km=req.max_distance_km,
    )

    return RelocationPlanResponse(
        status=opt_result["status"],
        message=opt_result["message"],
        assignments=opt_result["assignments"],
        unassigned_populations=opt_result["unassigned_populations"],
        total_evacuated=opt_result["total_evacuated"],
        total_unassigned=opt_result["total_unassigned"],
        optimization_summary=opt_result["optimization_summary"],
    )
