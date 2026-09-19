"""Tests for Community Communication Web App."""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_community_communications():
    """Test message posting, message listing, and emergency broadcasts."""
    # 1. Post Announcement
    post_res = client.post(
        "/api/v1/communications/messages",
        json={
            "category": "WEATHER",
            "title": "Heavy Downpour Advisory",
            "message": "Continuous rainfall expected for next 12 hours.",
            "target_area": "Wayanad Sector 1",
            "severity": "WARNING",
        },
    )
    assert post_res.status_code == 201
    msg = post_res.json()
    assert msg["category"] == "WEATHER"

    # 2. Get Messages Filtered
    list_res = client.get("/api/v1/communications/messages?category=WEATHER")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Dispatch Emergency Broadcast
    broadcast_res = client.post(
        "/api/v1/communications/emergency-broadcast",
        json={
            "title": "MANDATORY EVACUATION ORDER",
            "message": "Evacuate immediately to designated shelters.",
            "target_area": "Chooralmala Red Zone",
            "category": "EMERGENCY",
            "severity": "CRITICAL",
        },
    )
    assert broadcast_res.status_code == 200
    b_data = broadcast_res.json()
    assert "dispatch_details" in b_data
