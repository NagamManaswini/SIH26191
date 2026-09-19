"""Coordinate Reference System (CRS) projection utilities using PyProj and GeoPandas."""

from typing import Union
import geopandas as gpd
from pyproj import CRS, Transformer
from shapely.geometry import base, shape, mapping

DEFAULT_CRS = "EPSG:4326"


def ensure_epsg4326(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Ensure a GeoDataFrame is projected in EPSG:4326 (WGS84 lat/lon)."""
    if gdf is None or gdf.empty:
        return gdf
    if gdf.crs is None:
        gdf = gdf.set_crs(DEFAULT_CRS)
    elif gdf.crs.to_string() != DEFAULT_CRS and gdf.crs != CRS.from_epsg(4326):
        gdf = gdf.to_crs(DEFAULT_CRS)
    return gdf


def transform_coordinates(
    x: float, y: float, source_crs: str = "EPSG:4326", target_crs: str = "EPSG:4326"
) -> tuple[float, float]:
    """Transform point coordinates between coordinate systems."""
    if source_crs == target_crs:
        return x, y
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    tx, ty = transformer.transform(x, y)
    return float(tx), float(ty)
