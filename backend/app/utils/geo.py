"""Geospatial helper utilities for formatting WKT, GeoJSON, and coordinate processing."""

import json
from typing import Any, Dict, List, Optional, Tuple, Union
from shapely.geometry import Point, Polygon, LineString, shape, mapping
from shapely.wkt import loads as wkt_loads, dumps as wkt_dumps


def coords_to_point_wkt(longitude: float, latitude: float) -> str:
    """Convert longitude and latitude to POINT WKT string."""
    return f"POINT({longitude} {latitude})"


def point_wkt_to_coords(wkt_str: str) -> Optional[Tuple[float, float]]:
    """Parse POINT WKT string and return (longitude, latitude)."""
    if not wkt_str:
        return None
    try:
        if isinstance(wkt_str, str) and wkt_str.startswith("POINT"):
            geom = wkt_loads(wkt_str)
            return (float(geom.x), float(geom.y))
        elif hasattr(wkt_str, "x") and hasattr(wkt_str, "y"):
            return (float(wkt_str.x), float(wkt_str.y))
    except Exception:
        pass
    return None


def polygon_wkt_to_centroid(wkt_str: str) -> Optional[Tuple[float, float]]:
    """Parse POLYGON WKT string and return centroid (longitude, latitude)."""
    if not wkt_str:
        return None
    try:
        if isinstance(wkt_str, str):
            geom = wkt_loads(wkt_str)
            centroid = geom.centroid
            return (float(centroid.x), float(centroid.y))
    except Exception:
        pass
    return None


def polygon_coords_to_wkt(coordinates: List[List[Tuple[float, float]]]) -> str:
    """Convert polygon outer/inner ring coordinate list to POLYGON WKT string."""
    poly = Polygon(coordinates[0], coordinates[1:] if len(coordinates) > 1 else None)
    return wkt_dumps(poly)


def linestring_coords_to_wkt(coordinates: List[Tuple[float, float]]) -> str:
    """Convert coordinate list to LINESTRING WKT string."""
    ls = LineString(coordinates)
    return wkt_dumps(ls)


def parse_geometry_to_geojson(geom_input: Any) -> Optional[Dict[str, Any]]:
    """Convert WKT string, Shapely geometry, or GeoAlchemy Element to GeoJSON dict."""
    if geom_input is None:
        return None
    try:
        if isinstance(geom_input, str):
            shapely_geom = wkt_loads(geom_input)
            return mapping(shapely_geom)
        elif hasattr(geom_input, "data"):
            from geoalchemy2.shape import to_shape
            shapely_geom = to_shape(geom_input)
            return mapping(shapely_geom)
        elif hasattr(geom_input, "__geo_interface__"):
            return mapping(geom_input)
    except Exception:
        pass
    return None
