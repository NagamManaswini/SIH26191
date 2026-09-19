"""GIS Package for SIH26191 Intelligent Disaster Management Platform."""

from gis.loaders import load_raster_data, load_vector_dataset
from gis.processors import compute_slope_from_dem, validate_spatial_dataset, validate_coordinates
from gis.hazard import compute_baseline_hazard_score, analyze_grid_hazard_zones, HazardConfig
from gis.routing import build_road_network_graph, calculate_safe_evacuation_route
from gis.utils import ensure_epsg4326, sanitize_geometry, geodataframe_to_geojson

__all__ = [
    "load_raster_data",
    "load_vector_dataset",
    "compute_slope_from_dem",
    "validate_spatial_dataset",
    "validate_coordinates",
    "compute_baseline_hazard_score",
    "analyze_grid_hazard_zones",
    "HazardConfig",
    "build_road_network_graph",
    "calculate_safe_evacuation_route",
    "ensure_epsg4326",
    "sanitize_geometry",
    "geodataframe_to_geojson",
]
