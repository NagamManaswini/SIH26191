import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analytics_summary_api():
    response = client.get("/api/analytics/summary?date_range=30d")
    assert response.status_code == 200
    data = response.json()
    assert "average_rainfall_mm" in data
    assert "maximum_rainfall_mm" in data
    assert "maximum_river_level_m" in data
    assert "average_soil_moisture_pct" in data
    assert "total_alerts_count" in data
    assert "critical_events_count" in data
    assert "sensor_uptime_pct" in data
    assert "prediction_metrics" in data
    assert data["prediction_metrics"]["rmse_m"] > 0
    assert data["prediction_metrics"]["nse_coefficient"] > 0.8

def test_analytics_charts_api():
    response = client.get("/api/analytics/charts?date_range=30d")
    assert response.status_code == 200
    data = response.json()
    assert "rainfall_history" in data
    assert "river_level_history" in data
    assert "soil_moisture_history" in data
    assert "historical_flood_events" in data
    assert "risk_distribution" in data
    assert "sensor_availability" in data
    assert "alert_frequency" in data
    assert "prediction_vs_actual" in data
    assert len(data["historical_flood_events"]) >= 3
    assert len(data["risk_distribution"]) == 4

def test_analytics_csv_export_api():
    response = client.get("/api/analytics/export/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "flash_flood_analytics_report.csv" in response.headers["content-disposition"]
    text = response.text
    assert "METRIC SUMMARY" in text
    assert "WATERSHED RISK METRICS" in text
    assert "IOT SENSOR NETWORK INVENTORY & HEALTH" in text
