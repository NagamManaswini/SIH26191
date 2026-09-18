import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_forecaster import ai_forecaster

client = TestClient(app)


def test_ai_feature_extraction():
    sample_rainfall = [{"rainfall_mm": 18.5}, {"rainfall_mm": 12.0}, {"rainfall_mm": 8.0}]
    sample_river = [{"water_level_m": 2.4}, {"water_level_m": 2.1}]
    sample_soil = [{"moisture_percentage": 74.5}]
    sample_meta = {"elevation_m": 1950.0, "average_slope_deg": 28.0, "area_sq_km": 150.0}

    features = ai_forecaster.extract_features(
        rainfall_records=sample_rainfall,
        river_records=sample_river,
        soil_records=sample_soil,
        watershed_meta=sample_meta,
        historical_events_count=2
    )

    for feat in ai_forecaster.FEATURE_NAMES:
        assert feat in features
        assert isinstance(features[feat], (int, float))

    assert features["rainfall_5min"] == 18.5
    assert features["river_level"] == 2.4
    assert features["river_rate_of_rise"] >= 0.0
    assert features["soil_moisture"] == 74.5
    assert features["slope"] == 28.0


def test_multi_horizon_prediction_logic():
    sample_features = {
        "rainfall_5min": 35.0,
        "rainfall_15min": 25.0,
        "rainfall_30min": 18.0,
        "rainfall_60min": 12.0,
        "accumulated_rainfall": 55.0,
        "river_level": 2.2,
        "river_rate_of_rise": 0.45,
        "soil_moisture": 78.0,
        "elevation": 1850.0,
        "slope": 26.0,
        "historical_risk": 50.0
    }

    predictions = ai_forecaster.predict_multi_horizon(sample_features)
    assert len(predictions) == 4
    
    horizons = [p["minutes_ahead"] for p in predictions]
    assert horizons == [30, 60, 90, 120]

    for p in predictions:
        assert p["predicted_water_level"] > 0
        assert 0 <= p["flood_probability"] <= 100
        assert p["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
        assert 0 <= p["confidence"] <= 100
        assert p["confidence_lower"] <= p["predicted_water_level"] <= p["confidence_upper"]


def test_get_watershed_predictions_api():
    response = client.get("/api/predictions/watershed/1")
    assert response.status_code == 200
    data = response.json()

    assert data["watershed_id"] == 1
    assert "watershed_name" in data
    assert "current_water_level" in data
    assert "predictions" in data
    assert len(data["predictions"]) == 4

    pred_30 = data["predictions"][0]
    assert pred_30["minutes_ahead"] == 30
    assert "predicted_water_level" in pred_30
    assert "flood_probability" in pred_30
    assert "risk_level" in pred_30
    assert "confidence" in pred_30
    assert "confidence_lower" in pred_30
    assert "confidence_upper" in pred_30

    assert "model_metadata" in data
    assert "model_version" in data
    assert "disclaimer" in data["model_metadata"]


def test_post_generate_predictions_api():
    response = client.post("/api/predictions/generate", json={
        "watershed_id": 1,
        "persist": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["watershed_id"] == 1


def test_get_all_predictions_api():
    response = client.get("/api/predictions/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    for item in data:
        assert "watershed_id" in item
        assert "predictions" in item
        assert len(item["predictions"]) == 4


def test_get_model_metadata_api():
    response = client.get("/api/predictions/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert "training_date" in data
    assert "features_used" in data
    assert len(data["features_used"]) == 11
    assert "disclaimer" in data
