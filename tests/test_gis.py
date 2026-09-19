"""Automated unit and integration test suite for GIS processing and baseline hazard engine."""

import os
import pytest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString

from gis.loaders.raster_loader import load_raster_data
from gis.loaders.vector_loader import load_vector_dataset
from gis.processors.terrain import compute_slope_from_dem, normalize_terrain_factor
from gis.processors.spatial_validator import (
    validate_spatial_dataset,
    validate_coordinates,
    SpatialValidationError,
)
from gis.hazard.config import HazardConfig, default_hazard_config
from gis.hazard.baseline_engine import compute_baseline_hazard_score, analyze_grid_hazard_zones
from gis.utils.crs import ensure_epsg4326, transform_coordinates
from gis.utils.geo_format import sanitize_geometry, geodataframe_to_geojson


def test_crs_conversion():
    """Verify CRS transformation and GeoDataFrame projection to EPSG:4326."""
    # Create GeoDataFrame in UTM zone 43N (EPSG:32643)
    p = Point(300000, 2100000)
    gdf_utm = gpd.GeoDataFrame({"name": ["UTM Point"]}, geometry=[p], crs="EPSG:32643")
    
    gdf_4326 = ensure_epsg4326(gdf_utm)
    assert gdf_4326.crs.to_string() == "EPSG:4326"
    assert -180.0 <= gdf_4326.geometry.iloc[0].x <= 180.0
    assert -90.0 <= gdf_4326.geometry.iloc[0].y <= 90.0


def test_coordinate_validation():
    """Verify valid and invalid latitude/longitude coordinate bounds."""
    assert validate_coordinates(72.85, 19.05) is True
    assert validate_coordinates(-190.0, 19.05) is False  # lon out of bounds
    assert validate_coordinates(72.85, 95.0) is False   # lat out of bounds
    assert validate_coordinates(None, 19.05) is False


def test_invalid_geometry_sanitization():
    """Verify self-intersecting / invalid polygons are sanitized using Shapely make_valid."""
    # Bow-tie self-intersecting polygon
    invalid_poly = Polygon([(0, 0), (0, 2), (2, 0), (2, 2), (0, 0)])
    assert not invalid_poly.is_valid

    sanitized = sanitize_geometry(invalid_poly)
    assert sanitized is not None
    assert sanitized.is_valid


def test_missing_data_and_empty_dataset_handling():
    """Verify spatial validator handles empty datasets and missing attributes cleanly."""
    empty_gdf = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
    
    # Should return empty GDF when allow_empty=True
    validated = validate_spatial_dataset(empty_gdf, allow_empty=True)
    assert validated.empty

    # Should raise error when allow_empty=False
    with pytest.raises(SpatialValidationError):
        validate_spatial_dataset(empty_gdf, allow_empty=False)

    # Missing column check
    valid_gdf = gpd.GeoDataFrame({"geometry": [Point(72.85, 19.05)]}, crs="EPSG:4326")
    with pytest.raises(SpatialValidationError):
        validate_spatial_dataset(valid_gdf, required_columns=["elevation"], allow_empty=False)


def test_slope_computation_from_dem():
    """Verify calculation of slope degrees from synthetic elevation matrix."""
    # Flat elevation DEM
    flat_dem = np.full((10, 10), 100.0, dtype=np.float32)
    flat_slope = compute_slope_from_dem(flat_dem)
    assert np.allclose(flat_slope, 0.0)

    # Steep elevation DEM (gradient from 0 to 500 meters over 10 cells)
    steep_dem = np.tile(np.linspace(0, 500, 10), (10, 1)).astype(np.float32)
    steep_slope = compute_slope_from_dem(steep_dem, cellsize_meters=100.0)
    assert np.mean(steep_slope) > 10.0


def test_baseline_hazard_categories():
    """Verify hazard score computation and categorization into LOW, MODERATE, HIGH, CRITICAL."""
    cfg = default_hazard_config

    # Low risk parameters
    res_low = compute_baseline_hazard_score(rainfall_mm=10.0, slope_deg=2.0, elevation_m=50.0, config=cfg)
    assert res_low["category"] == "LOW"
    assert res_low["hazard_score"] < 0.25

    # Moderate risk parameters
    res_mod = compute_baseline_hazard_score(rainfall_mm=100.0, slope_deg=15.0, elevation_m=400.0, config=cfg)
    assert res_mod["category"] in ["MODERATE", "HIGH"]

    # Critical risk parameters (extreme rainfall + steep slope)
    res_crit = compute_baseline_hazard_score(rainfall_mm=300.0, slope_deg=45.0, elevation_m=1500.0, historical_event_count=5, config=cfg)
    assert res_crit["category"] == "CRITICAL"
    assert res_crit["hazard_score"] >= 0.75


def test_load_demo_raster_and_vector_datasets():
    """Verify loading demo GeoTIFF raster and GeoJSON datasets generated in data/demo."""
    dem_path = os.path.join("data", "demo", "elevation_dem.tif")
    if os.path.exists(dem_path):
        raster_info = load_raster_data(dem_path)
        assert raster_info["data"] is not None
        assert raster_info["shape"] == (50, 50)

    shelters_path = os.path.join("data", "demo", "shelters.geojson")
    if os.path.exists(shelters_path):
        gdf_shelters = load_vector_dataset(shelters_path)
        assert not gdf_shelters.empty
        assert gdf_shelters.crs.to_string() == "EPSG:4326"
