from typing import List, Optional, Dict, Any
import os
import json
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.hazard_zone import (
    HazardZoneCreate,
    HazardZoneUpdate,
    HazardZoneResponse,
    HazardAnalyzeRequest,
    GeoJSONFeatureCollection,
)
from backend.app.services.hazard_zone_service import (
    create_hazard_zone,
    get_hazard_zones,
    get_hazard_zone_by_id,
    update_hazard_zone,
    delete_hazard_zone,
)
from gis.hazard.baseline_engine import analyze_grid_hazard_zones, compute_baseline_hazard_score
from gis.hazard.config import HazardConfig

router = APIRouter(prefix="/hazards", tags=["Hazards"])


@router.get("", response_model=List[HazardZoneResponse])
def list_hazards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    risk_level: Optional[str] = Query(None, description="RED, YELLOW, GREEN, or CRITICAL"),
    db: Session = Depends(get_db),
):
    """Retrieve list of hazards with optional risk level filtering."""
    return get_hazard_zones(db=db, skip=skip, limit=limit, risk_level=risk_level)


@router.get("/map", response_model=Dict[str, Any])
def get_hazards_map(
    risk_level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Return active hazard zones as valid GeoJSON FeatureCollection for interactive map rendering."""
    hazards = get_hazard_zones(db=db, skip=0, limit=500, risk_level=risk_level)
    features = []

    for h in hazards:
        coords = h.coordinates
        if not coords:
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": coords
            },
            "properties": {
                "id": h.id,
                "name": h.name,
                "hazard_type": h.hazard_type,
                "risk_level": h.risk_level,
                "risk_score": h.risk_score,
                "created_at": str(h.created_at) if h.created_at else None
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/{hazard_id}", response_model=HazardZoneResponse)
def get_hazard(hazard_id: int, db: Session = Depends(get_db)):
    """Get a specific hazard zone by ID."""
    return get_hazard_zone_by_id(db=db, hazard_id=hazard_id)


@router.post("", response_model=HazardZoneResponse, status_code=status.HTTP_201_CREATED)
def create_new_hazard(hazard_in: HazardZoneCreate, db: Session = Depends(get_db)):
    """Create a new hazard zone record."""
    return create_hazard_zone(db=db, hazard_in=hazard_in)


@router.put("/{hazard_id}", response_model=HazardZoneResponse)
def update_existing_hazard(
    hazard_id: int, hazard_in: HazardZoneUpdate, db: Session = Depends(get_db)
):
    """Update a hazard zone record."""
    return update_hazard_zone(db=db, hazard_id=hazard_id, hazard_in=hazard_in)


@router.delete("/{hazard_id}", status_code=status.HTTP_200_OK)
def remove_hazard(hazard_id: int, db: Session = Depends(get_db)):
    """Delete a hazard zone record."""
    return delete_hazard_zone(db=db, hazard_id=hazard_id)


@router.post("/analyze", response_model=List[HazardZoneResponse], status_code=status.HTTP_200_OK)
def analyze_hazards(req: HazardAnalyzeRequest, db: Session = Depends(get_db)):
    """Trigger GIS baseline hazard analysis using elevation DEM grid and rainfall parameters."""
    cfg = HazardConfig(
        weight_rainfall=req.weight_rainfall,
        weight_slope=req.weight_slope,
        threshold_low=req.threshold_low,
        threshold_moderate=req.threshold_moderate,
        threshold_high=req.threshold_high,
    )

    demo_grid_path = os.path.join("data", "demo", "elevation_slope_grid.geojson")
    grid_geojson = {"type": "FeatureCollection", "features": []}
    if os.path.exists(demo_grid_path):
        with open(demo_grid_path, "r") as f:
            grid_geojson = json.load(f)

    gdf = analyze_grid_hazard_zones(
        elevation_slope_grid=grid_geojson,
        rainfall_mm=req.rainfall_mm,
        config=cfg,
    )

    created_hazards = []
    # Filter top high/critical risk cells to record as hazard zones
    if not gdf.empty:
        high_risk_gdf = gdf[gdf["hazard_score"] >= req.threshold_low]
        # Limit to top 20 zones for clean prototype persistence
        for idx, row in high_risk_gdf.head(20).iterrows():
            geom = row["geometry"]
            coords = [list(geom.exterior.coords)] if hasattr(geom, "exterior") else []

            create_schema = HazardZoneCreate(
                name=f"{req.region_name} - {row['hazard_category']} Zone {idx+1}",
                hazard_type="combined_landslide_flood",
                risk_level=row["hazard_category"],
                risk_score=float(row["hazard_score"]),
                coordinates=coords,
            )
            created = create_hazard_zone(db=db, hazard_in=create_schema)
            created_hazards.append(created)

    return created_hazards
