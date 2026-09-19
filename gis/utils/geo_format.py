"""Geometry formatting, validation, and GeoJSON conversion utilities."""

from typing import Any, Dict, Optional
import json
import geopandas as gpd
from shapely.geometry import shape, mapping
from shapely.validation import make_valid


def sanitize_geometry(geom_obj: Any) -> Optional[Any]:
    """Validate and fix invalid geometries using Shapely make_valid."""
    if geom_obj is None:
        return None
    try:
        if isinstance(geom_obj, dict):
            s_geom = shape(geom_obj)
        else:
            s_geom = geom_obj

        if not s_geom.is_valid:
            s_geom = make_valid(s_geom)
        return s_geom
    except Exception:
        return None


def geodataframe_to_geojson(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Convert a GeoDataFrame into standard GeoJSON FeatureCollection dict."""
    if gdf is None or gdf.empty:
        return {"type": "FeatureCollection", "features": []}
    return json.loads(gdf.to_json())
