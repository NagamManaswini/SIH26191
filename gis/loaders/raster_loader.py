"""Raster dataset loader using Rasterio."""

import os
from typing import Dict, Any, Tuple, Optional
import numpy as np
import rasterio


def load_raster_data(file_path: str) -> Dict[str, Any]:
    """Load a single-band raster file (e.g. DEM GeoTIFF) and return data array, transform, crs, and bounds."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raster file not found: {file_path}")

    with rasterio.open(file_path) as src:
        array = src.read(1)
        nodata = src.nodata
        
        # Replace nodata values with NaN for clean numpy math
        data = array.astype(np.float32)
        if nodata is not None:
            data[data == nodata] = np.nan

        return {
            "data": data,
            "crs": str(src.crs),
            "bounds": src.bounds,
            "transform": src.transform,
            "shape": src.shape,
            "width": src.width,
            "height": src.height,
        }
