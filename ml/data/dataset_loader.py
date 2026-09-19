"""Synthetic Training Dataset Loader for ML Hazard Model.

DATASET DOCUMENTATION & PROTOTYPE DISCLAIMER:
---------------------------------------------
This module generates and loads synthetic training samples based on the project's demo dataset.
Features marked as [DEMO / SYNTHETIC] are designed as drop-in interfaces for production datasets:

1. rainfall_mm [SYNTHETIC] -> Replacement: IMD / GPM Satellite 1km gridded rainfall.
2. rainfall_intensity_score [SYNTHETIC] -> Replacement: IMD hourly storm intensity radar.
3. slope_deg [SYNTHETIC] -> Replacement: ISRO Cartosat-3 / SRTM 30m DEM slope.
4. elevation_m [SYNTHETIC] -> Replacement: ISRO Bhuvan / ALOS World 3D DEM.
5. soil_erodibility [SYNTHETIC] -> Replacement: NBSS&LUP Soil Erodibility K-factor.
6. land_use_runoff_factor [SYNTHETIC] -> Replacement: Sentinel-2 / ESA 10m LULC map.
7. historical_disaster_count [SYNTHETIC] -> Replacement: NDMA/ISRO historical hazard inventory.
"""

import os
import json
import numpy as np
import pandas as pd


def generate_synthetic_training_dataframe(num_samples: int = 3000, seed: int = 42) -> pd.DataFrame:
    """Generate a realistic synthetic DataFrame modeling disaster risk for training XGBoost model.

    Correctly models clear/low-rainfall weather (0-25mm) as LOW risk level.
    """
    np.random.seed(seed)

    # 45% of samples are clear/normal weather (0 - 20mm rain), 55% moderate-to-extreme rain
    is_clear = np.random.uniform(0, 1, num_samples) < 0.45
    rainfall_mm = np.where(
        is_clear,
        np.random.uniform(0.0, 20.0, num_samples),
        np.random.uniform(20.0, 380.0, num_samples)
    )

    slope_deg = np.random.uniform(0.0, 50.0, num_samples)
    elevation_m = np.random.uniform(10.0, 1800.0, num_samples)
    soil_erodibility = np.random.uniform(0.1, 0.95, num_samples)
    land_use_runoff = np.random.choice([0.2, 0.45, 0.70, 0.90], size=num_samples)
    historical_count = np.random.poisson(lam=0.5, size=num_samples)
    historical_count = np.clip(historical_count, 0, 5)

    # Intensity score mapping
    intensity_score = np.where(
        rainfall_mm < 25.0, 0.10,
        np.where(rainfall_mm < 90.0, 0.40,
        np.where(rainfall_mm < 200.0, 0.75, 1.0))
    )

    # Calculate ground-truth risk score (physics-informed: clear weather = LOW risk)
    rain_factor = (rainfall_mm / 350.0)
    slope_factor = (slope_deg / 50.0)

    raw_risk = (
        0.55 * rain_factor
        + 0.25 * slope_factor
        + 0.12 * intensity_score
        + 0.04 * soil_erodibility
        + 0.04 * (historical_count / 5.0)
        + np.random.normal(0, 0.02, num_samples)
    )

    risk_score = np.clip(raw_risk, 0.0, 1.0)

    # Target categories: 0=LOW, 1=MODERATE, 2=HIGH, 3=CRITICAL
    risk_category = np.where(
        risk_score < 0.25, 0,
        np.where(risk_score < 0.50, 1,
        np.where(risk_score < 0.75, 2, 3))
    )

    df = pd.DataFrame(
        {
            "rainfall_mm": rainfall_mm,
            "rainfall_intensity_score": intensity_score,
            "slope_deg": slope_deg,
            "elevation_m": elevation_m,
            "soil_erodibility": soil_erodibility,
            "land_use_runoff_factor": land_use_runoff,
            "historical_disaster_count": historical_count,
            "risk_score": risk_score,
            "risk_category": risk_category,
        }
    )

    return df
