"""Automated unit and integration test suite for ML Risk Prediction pipeline."""

import os
import pytest
import numpy as np

from ml.features.feature_extractor import (
    extract_features_from_dict,
    map_rainfall_intensity,
    map_land_use_factor,
    FEATURE_NAMES,
)
from ml.data.dataset_loader import generate_synthetic_training_dataframe
from ml.evaluation.metrics import evaluate_model_performance
from ml.inference.predictor import HazardPredictor, get_predictor


def test_synthetic_dataset_generation():
    """Verify synthetic dataset generator creates required feature columns and target categories."""
    df = generate_synthetic_training_dataframe(num_samples=100, seed=123)
    assert not df.empty
    assert len(df) == 100
    for col in FEATURE_NAMES:
        assert col in df.columns
    assert "risk_category" in df.columns
    assert set(df["risk_category"].unique()).issubset({0, 1, 2, 3})


def test_feature_extraction_and_mapping():
    """Verify mapping of categorical values and extraction of feature vector."""
    assert map_rainfall_intensity("heavy") == 0.75
    assert map_rainfall_intensity("EXTREME") == 1.0
    assert map_land_use_factor("dense_forest") == 0.25

    raw_input = {
        "rainfall_mm": 180.0,
        "rainfall_intensity": "heavy",
        "slope_deg": 35.0,
        "elevation_m": 800.0,
        "soil_erodibility": 0.8,
        "land_use_type": "steep_barren",
        "historical_disasters": 2,
    }
    vec = extract_features_from_dict(raw_input)
    assert vec.shape == (1, 7)
    assert vec[0][0] == 180.0
    assert vec[0][1] == 0.75  # heavy intensity score
    assert vec[0][2] == 35.0


def test_invalid_feature_input_raises_error():
    """Verify feature extractor raises ValueError for invalid / out-of-bounds parameters."""
    with pytest.raises(ValueError, match="rainfall_mm cannot be negative"):
        extract_features_from_dict({"rainfall_mm": -10.0})

    with pytest.raises(ValueError, match="slope_deg must be between"):
        extract_features_from_dict({"slope_deg": 120.0})

    with pytest.raises(ValueError, match="Invalid rainfall intensity"):
        extract_features_from_dict({"rainfall_intensity": "catastrophic"})


def test_model_loading_and_inference():
    """Verify HazardPredictor model loading and inference execution."""
    predictor = get_predictor()
    assert predictor.model is not None
    assert predictor.scaler is not None

    sample_input = {
        "rainfall_mm": 220.0,
        "rainfall_intensity": "heavy",
        "slope_deg": 40.0,
        "elevation_m": 950.0,
        "soil_erodibility": 0.85,
        "land_use_type": "steep_barren",
        "historical_disasters": 3,
    }

    result = predictor.predict(sample_input)
    assert "risk_score" in result
    assert "risk_category" in result
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_category"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert "model_version" in result
    assert "PROTOTYPE DEMO MODEL" in result["disclaimer"]


def test_evaluation_metrics_calculator():
    """Verify calculation of model performance evaluation metrics."""
    y_true = np.array([0, 1, 2, 3, 1, 2])
    y_pred = np.array([0, 1, 2, 3, 1, 2])
    metrics = evaluate_model_performance(y_true, y_pred)
    assert metrics["accuracy"] == 1.0
    assert metrics["f1_score"] == 1.0
