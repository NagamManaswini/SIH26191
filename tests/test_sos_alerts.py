"""Tests for Emergency SOS Sound Alert System."""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_trigger_manual_sos():
    """Test triggering manual SOS sound alert."""
    response = client.post(
        "/api/v1/alerts/sos-trigger",
        params={
            "title": "TEST SOS ALARM",
            "message": "Test manual emergency trigger",
            "affected_area": "Chooralmala Sector",
            "performed_by": "Test Officer",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SOS_ACTIVE"
    assert data["severity"] == "CRITICAL"
    assert data["sos_sound_required"] is True


def test_stop_manual_sos():
    """Test stopping manual SOS alert."""
    response = client.post(
        "/api/v1/alerts/sos-stop/1",
        params={"performed_by": "Test Officer"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SOS_STOPPED"


def test_alert_audit_logs():
    """Test fetching alert audit logs."""
    response = client.get("/api/v1/alerts/audit-logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
