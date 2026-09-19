"""Baseline hazard analysis engine combining terrain, rainfall, soil, and historical disaster factors."""

from typing import Dict, Any, List, Optional
import numpy as np
import geopandas as gpd
from shapely.geometry import shape, Polygon, mapping, Point

from gis.hazard.config import HazardConfig, default_hazard_config
from gis.processors.spatial_validator import validate_spatial_dataset, validate_coordinates
from gis.utils.geo_format import sanitize_geometry, geodataframe_to_geojson


def compute_baseline_hazard_score(
    rainfall_mm: float = 0.0,
    slope_deg: float = 0.0,
    elevation_m: float = 0.0,
    soil_erodibility: float = 0.5,
    historical_event_count: int = 0,
    config: Optional[HazardConfig] = None,
) -> Dict[str, Any]:
    """Compute baseline hazard score and category for a single location / cell."""
    cfg = config or default_hazard_config

    # Normalize individual factor scores (0.0 to 1.0)
    # 1. Rainfall score (0 - 300 mm scale)
    f_rainfall = float(np.clip(rainfall_mm / 300.0, 0.0, 1.0))
    # 2. Slope score (0 - 45 degrees scale)
    f_slope = float(np.clip(slope_deg / 45.0, 0.0, 1.0))
    # 3. Elevation score (steep high elevation hazard 0 - 2000m scale)
    f_elevation = float(np.clip(elevation_m / 2000.0, 0.0, 1.0))
    # 4. Soil erodibility factor (0.0 - 1.0)
    f_soil = float(np.clip(soil_erodibility, 0.0, 1.0))
    # 5. Historical events factor (0 - 5 events scale)
    f_historical = float(np.clip(historical_event_count / 5.0, 0.0, 1.0))

    # Weighted sum calculation
    raw_score = (
        cfg.weight_rainfall * f_rainfall
        + cfg.weight_slope * f_slope
        + cfg.weight_elevation * f_elevation
        + cfg.weight_soil * f_soil
        + cfg.weight_historical * f_historical
    )

    hazard_score = float(round(np.clip(raw_score, 0.0, 1.0), 4))
    category = cfg.classify_score(hazard_score)

    return {
        "hazard_score": hazard_score,
        "category": category,
        "factors": {
            "rainfall_factor": round(f_rainfall, 4),
            "slope_factor": round(f_slope, 4),
            "elevation_factor": round(f_elevation, 4),
            "soil_factor": round(f_soil, 4),
            "historical_factor": round(f_historical, 4),
        },
    }


def analyze_grid_hazard_zones(
    elevation_slope_grid: Dict[str, Any],
    rainfall_mm: float = 120.0,
    config: Optional[HazardConfig] = None,
) -> gpd.GeoDataFrame:
    """Analyze a spatial grid GeoJSON dataset and return a GeoDataFrame of hazard polygons with scores."""
    cfg = config or default_hazard_config
    features = elevation_slope_grid.get("features", [])

    rows = []
    for f in features:
        props = f.get("properties", {})
        geom_dict = f.get("geometry")
        s_geom = sanitize_geometry(geom_dict)
        if s_geom is None or not s_geom.is_valid:
            continue

        elev = float(props.get("elevation_m", 100.0))
        slope = float(props.get("slope_deg", 10.0))

        res = compute_baseline_hazard_score(
            rainfall_mm=rainfall_mm,
            slope_deg=slope,
            elevation_m=elev,
            soil_erodibility=0.5,
            historical_event_count=1 if slope > 30 else 0,
            config=cfg,
        )

        rows.append(
            {
                "geometry": s_geom,
                "cell_id": props.get("cell_id", ""),
                "elevation_m": elev,
                "slope_deg": slope,
                "rainfall_mm": rainfall_mm,
                "hazard_score": res["hazard_score"],
                "hazard_category": res["category"],
            }
        )

    if not rows:
        return gpd.GeoDataFrame(columns=["geometry", "hazard_score", "hazard_category"], crs="EPSG:4326")

    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    return validate_spatial_dataset(gdf, allow_empty=True)
