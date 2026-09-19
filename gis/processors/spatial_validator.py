"""Spatial data validator for handling invalid geometries, missing data, empty datasets, and CRS check."""

from typing import Dict, Any, List, Optional
import geopandas as gpd
from shapely.geometry import base, shape
from gis.utils.crs import ensure_epsg4326
from gis.utils.geo_format import sanitize_geometry


class SpatialValidationError(Exception):
    """Custom exception raised when spatial validation fails."""
    pass


def validate_spatial_dataset(
    gdf: Optional[gpd.GeoDataFrame],
    required_columns: Optional[List[str]] = None,
    allow_empty: bool = False
) -> gpd.GeoDataFrame:
    """Validate a GeoDataFrame for valid geometries, non-empty status, CRS, and required columns."""
    if gdf is None:
        if allow_empty:
            return gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
        raise SpatialValidationError("Spatial dataset is None")

    if gdf.empty and not allow_empty:
        raise SpatialValidationError("Spatial dataset is empty")

    if required_columns:
        for col in required_columns:
            if col not in gdf.columns:
                raise SpatialValidationError(f"Missing required spatial attribute column: '{col}'")

    # Ensure EPSG:4326
    gdf = ensure_epsg4326(gdf)

    # Sanitize invalid geometries
    if not gdf.empty and "geometry" in gdf.columns:
        gdf["geometry"] = gdf["geometry"].apply(sanitize_geometry)
        # Drop rows where geometry remains null or invalid
        gdf = gdf[gdf["geometry"].notnull() & gdf["geometry"].is_valid]

    return gdf


def validate_coordinates(longitude: float, latitude: float) -> bool:
    """Verify if longitude (-180 to 180) and latitude (-90 to 90) coordinates are valid."""
    if longitude is None or latitude is None:
        return False
    if not (-180.0 <= float(longitude) <= 180.0):
        return False
    if not (-90.0 <= float(latitude) <= 90.0):
        return False
    return True
