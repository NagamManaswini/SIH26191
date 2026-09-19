"""Integration tests for Live Weather API and RBAC PDF Report Generation."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_live_weather_api():
    """Test dynamic live weather endpoint for Chennai coordinates."""
    response = client.get("/api/v1/weather/live?lat=13.0827&lon=80.2707&location_name=Chennai")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "data_status" in data
    assert data["latitude"] == 13.0827
    assert data["longitude"] == 80.2707
    assert "last_updated" in data


def test_pdf_report_admin_access():
    """Test PDF report generation succeeds for ADMIN user role."""
    payload = {
        "location_name": "Chennai Sector",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "admin_name": "Test Administrator",
    }
    headers = {"X-User-Role": "admin"}
    response = client.post("/api/v1/reports/generate", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 1000  # Non-empty PDF binary file


def test_pdf_report_user_forbidden():
    """Test PDF report generation is STRICTLY FORBIDDEN (403) for normal USER role."""
    payload = {
        "location_name": "Chennai Sector",
        "latitude": 13.0827,
        "longitude": 80.2707,
    }
    headers = {"X-User-Role": "user"}
    response = client.post("/api/v1/reports/generate", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
