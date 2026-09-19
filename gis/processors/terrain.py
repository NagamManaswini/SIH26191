"""Terrain analysis processor (slope, aspect, elevation profiles)."""

from typing import Dict, Any
import numpy as np


def compute_slope_from_dem(elevation_matrix: np.ndarray, cellsize_meters: float = 100.0) -> np.ndarray:
    """Calculate slope matrix in degrees from an elevation DEM matrix."""
    if elevation_matrix is None or elevation_matrix.size == 0:
        return np.array([[]], dtype=np.float32)

    # Clean NaNs or fill with nanmean for gradient calculation
    cleaned = np.nan_to_num(elevation_matrix, nan=np.nanmean(elevation_matrix) if not np.all(np.isnan(elevation_matrix)) else 0.0)
    
    dy, dx = np.gradient(cleaned, cellsize_meters)
    slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
    
    # Restore original NaNs
    slope[np.isnan(elevation_matrix)] = np.nan
    return slope.astype(np.float32)


def normalize_terrain_factor(matrix: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    """Normalize array values to a 0.0 - 1.0 factor range."""
    if matrix is None or matrix.size == 0:
        return matrix
    
    clipped = np.clip(matrix, min_val, max_val)
    rng = max_val - min_val
    if rng <= 0:
        return np.zeros_like(clipped, dtype=np.float32)
    
    return ((clipped - min_val) / rng).astype(np.float32)
