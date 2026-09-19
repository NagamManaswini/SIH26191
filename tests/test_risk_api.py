"""Automated test suite for ML Risk Prediction API endpoint POST /api/v1/risk/predict."""

import pytest


def test_predict_risk_valid_payload(client):
    payload = {
        "rainfall_mm": 190.0,
        "rainfall_intensity": "heavy",
        "slope_deg": 35.0,
        "elevation_m": 750.0,
        "soil_erodibility": 0.80,
        "land_use_type": "steep_barren",
        "historical_disasters": 2,
    }

    res = client.post("/api/v1/risk/predict", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "risk_score" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert data["risk_category"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert "class_probabilities" in data
    assert "feature_importances" in data
    assert "v1.0.0-prototype-demo" in data["model_version"]
    assert "PROTOTYPE DEMO MODEL" in data["disclaimer"]


def test_predict_risk_invalid_input_bad_request(client):
    invalid_payload = {
        "rainfall_mm": -50.0,  # Invalid negative rainfall caught by Pydantic ge=0.0
        "rainfall_intensity": "heavy",
        "slope_deg": 35.0,
        "elevation_m": 750.0,
    }

    res = client.post("/api/v1/risk/predict", json=invalid_payload)
    assert res.status_code == 422


def test_predict_risk_invalid_intensity_bad_request(client):
    invalid_payload = {
        "rainfall_mm": 100.0,
        "rainfall_intensity": "invalid_string_val",
        "slope_deg": 25.0,
        "elevation_m": 500.0,
    }

    res = client.post("/api/v1/risk/predict", json=invalid_payload)
    assert res.status_code == 400
    assert "Invalid rainfall intensity" in res.json()["detail"]
