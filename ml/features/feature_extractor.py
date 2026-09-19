"""Feature processing and validation module for ML hazard prediction."""

from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd

FEATURE_NAMES = [
    "rainfall_mm",
    "rainfall_intensity_score",
    "slope_deg",
    "elevation_m",
    "soil_erodibility",
    "land_use_runoff_factor",
    "historical_disaster_count",
]

INTENSITY_MAP = {
    "light": 0.25,
    "moderate": 0.50,
    "heavy": 0.75,
    "extreme": 1.0,
}

LAND_USE_MAP = {
    "dense_forest": 0.25,
    "agricultural": 0.45,
    "residential": 0.70,
    "steep_barren": 0.90,
    "mixed": 0.50,
}


def map_rainfall_intensity(intensity_str: str) -> float:
    """Convert rainfall intensity string into numeric score."""
    key = str(intensity_str).strip().lower()
    if key not in INTENSITY_MAP:
        raise ValueError(f"Invalid rainfall intensity '{intensity_str}'. Must be one of {list(INTENSITY_MAP.keys())}")
    return INTENSITY_MAP[key]


def map_land_use_factor(land_use_str: str) -> float:
    """Convert land-use type string into numeric runoff factor."""
    key = str(land_use_str).strip().lower()
    return LAND_USE_MAP.get(key, 0.50)


def extract_features_from_dict(raw_input: Dict[str, Any]) -> np.ndarray:
    """Extract and validate feature vector array from input dictionary."""
    rainfall_mm = float(raw_input.get("rainfall_mm", 0.0))
    if rainfall_mm < 0.0:
        raise ValueError("rainfall_mm cannot be negative.")

    slope_deg = float(raw_input.get("slope_deg", 0.0))
    if not (0.0 <= slope_deg <= 90.0):
        raise ValueError("slope_deg must be between 0.0 and 90.0 degrees.")

    elevation_m = float(raw_input.get("elevation_m", 0.0))
    if elevation_m < -500.0 or elevation_m > 9000.0:
        raise ValueError("elevation_m out of valid terrestrial bounds.")

    soil_erodibility = float(raw_input.get("soil_erodibility", 0.5))
    if not (0.0 <= soil_erodibility <= 1.0):
        raise ValueError("soil_erodibility must be between 0.0 and 1.0.")

    historical_count = int(raw_input.get("historical_disasters", raw_input.get("historical_disaster_count", 0)))
    if historical_count < 0:
        raise ValueError("historical_disasters count cannot be negative.")

    # Intensity mapping
    intensity_val = raw_input.get("rainfall_intensity", "moderate")
    if isinstance(intensity_val, (int, float)):
        intensity_score = float(intensity_val)
    else:
        intensity_score = map_rainfall_intensity(intensity_val)

    # Land use mapping
    land_use_val = raw_input.get("land_use_type", raw_input.get("land_use_runoff_factor", "mixed"))
    if isinstance(land_use_val, (int, float)):
        runoff_factor = float(land_use_val)
    else:
        runoff_factor = map_land_use_factor(land_use_val)

    feature_values = [
        rainfall_mm,
        intensity_score,
        slope_deg,
        elevation_m,
        soil_erodibility,
        runoff_factor,
        historical_count,
    ]

    return np.array([feature_values], dtype=np.float32)
