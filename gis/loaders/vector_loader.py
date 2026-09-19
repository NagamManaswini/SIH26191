"""Vector dataset loader using GeoPandas."""

import os
from typing import Optional
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from gis.utils.crs import ensure_epsg4326
from gis.utils.geo_format import sanitize_geometry


def load_vector_dataset(file_path: str, target_crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Load vector dataset from GeoJSON, Shapefile, or CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Vector dataset file not found: {file_path}")

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        if "longitude" in df.columns and "latitude" in df.columns:
            geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=target_crs)
        else:
            gdf = gpd.GeoDataFrame(df)
    else:
        gdf = gpd.read_file(file_path)

    if gdf is None or gdf.empty:
        return gpd.GeoDataFrame(columns=["geometry"], crs=target_crs)

    # Sanitize invalid geometries
    if "geometry" in gdf.columns:
        gdf["geometry"] = gdf["geometry"].apply(sanitize_geometry)
        gdf = gdf[gdf["geometry"].notnull()]

    gdf = ensure_epsg4326(gdf)
    return gdf
