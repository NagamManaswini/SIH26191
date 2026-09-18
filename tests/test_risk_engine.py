import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.risk_engine import risk_engine
from app.models.enums import RiskLevel

client = TestClient(app)


def test_individual_factor_scoring_functions():
    # 1. Rainfall score
    low_rain = risk_engine.score_rainfall_intensity(1.0)
    high_rain = risk_engine.score_rainfall_intensity(45.0)
    assert 0 <= low_rain <= 20
    assert 80 <= high_rain <= 100
    assert high_rain > low_rain

    # 2. River level score
    normal_riv = risk_engine.score_river_stage(1.2)
    danger_riv = risk_engine.score_river_stage(4.9)
    assert normal_riv <= 20
    assert danger_riv >= 85
    assert danger_riv > normal_riv

    # 3. Rate of rise score
    stable_rise = risk_engine.score_rate_of_rise(0.0)
    rapid_rise = risk_engine.score_rate_of_rise(0.65)
    assert stable_rise <= 10
    assert rapid_rise >= 85

    # 4. Soil moisture score
    dry_soil = risk_engine.score_soil_moisture(30.0)
    saturated_soil = risk_engine.score_soil_moisture(92.0)
    assert dry_soil <= 15
    assert saturated_soil >= 85

    # 5. Slope score
    flat_slope = risk_engine.score_slope(5.0)
    steep_slope = risk_engine.score_slope(35.0)
    assert flat_slope <= 25
    assert steep_slope >= 75


def test_risk_categorization():
    assert risk_engine.categorize_risk(15.0) == "LOW"
    assert risk_engine.categorize_risk(25.0) == "LOW"
    assert risk_engine.categorize_risk(26.0) == "MODERATE"
    assert risk_engine.categorize_risk(45.0) == "MODERATE"
    assert risk_engine.categorize_risk(50.0) == "MODERATE"
    assert risk_engine.categorize_risk(55.0) == "HIGH"
    assert risk_engine.categorize_risk(75.0) == "HIGH"
    assert risk_engine.categorize_risk(76.0) == "CRITICAL"
    assert risk_engine.categorize_risk(95.0) == "CRITICAL"


def test_get_watershed_risk_evaluation_api():
    response = client.get("/api/risk/watershed/1")
    assert response.status_code == 200
    data = response.json()
    
    assert data["watershed_id"] == 1
    assert "watershed_name" in data
    assert "risk_score" in data
    assert 0 <= data["risk_score"] <= 100
    assert data["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    
    # Factors
    factors = data["factors"]
    assert "rainfall" in factors
    assert "river_level" in factors
    assert "soil_moisture" in factors
    assert "slope" in factors
    assert "historical_risk" in factors
    assert "rate_of_rise" in factors

    # Factor attributes
    rf = factors["rainfall"]
    assert "score" in rf
    assert "weight" in rf
    assert "value" in rf
    assert "unit" in rf

    # Explanation list
    assert "explanation" in data
    assert isinstance(data["explanation"], list)
    assert len(data["explanation"]) >= 1

    # Historical comparison
    assert "historical_comparison" in data
    assert "past_events_count" in data["historical_comparison"]
    assert "recommendation" in data


def test_get_all_watersheds_risk_matrix():
    response = client.get("/api/risk/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    for item in data:
        assert "watershed_id" in item
        assert "risk_score" in item
        assert "risk_level" in item


def test_get_and_update_risk_configuration():
    # Get config
    get_res = client.get("/api/risk/configuration")
    assert get_res.status_code == 200
    config_data = get_res.json()
    assert "weights" in config_data
    assert "rainfall" in config_data["weights"]
    assert "thresholds" in config_data

    # Update weights
    put_res = client.put("/api/risk/configuration", json={
        "weight_rainfall": 0.30,
        "weight_river_level": 0.25
    })
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["weights"]["rainfall"] == 0.30
    assert updated["weights"]["river_level"] == 0.25
