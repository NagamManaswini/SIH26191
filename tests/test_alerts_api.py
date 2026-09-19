"""Automated integration test suite for Alert Management System REST API endpoints."""


def test_create_alert_api_endpoint(client):
    payload = {
        "title": "RED FLASH FLOOD ALERT",
        "message": "Monsoon rainfall spike 200mm. Evacuate immediately.",
        "severity": "CRITICAL",
        "affected_area": "Riverside Sector B",
        "recommended_action": "Proceed to North Ridge Community Stadium.",
        "status": "ACTIVE",
    }

    res = client.post("/api/v1/alerts", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["id"] is not None
    assert data["severity"] == "CRITICAL"
    assert data["status"] == "ACTIVE"
    assert "notification_dispatches" in data
    assert len(data["notification_dispatches"]) == 4  # Web, Email, Push, SMS


def test_list_alerts_api_endpoint(client):
    res = client.get("/api/v1/alerts")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_patch_alert_status_api_endpoint(client):
    # 1. Create alert
    payload = {
        "title": "Road Closure Advisory",
        "message": "Expressway closed for debris clearance.",
        "severity": "WARNING",
        "affected_area": "Expressway Km 45",
        "recommended_action": "Follow traffic police detours.",
        "status": "ACTIVE",
    }
    create_res = client.post("/api/v1/alerts", json=payload)
    alert_id = create_res.json()["id"]

    # 2. Patch status to ACKNOWLEDGED
    patch_res = client.patch(f"/api/v1/alerts/{alert_id}", json={"status": "ACKNOWLEDGED"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "ACKNOWLEDGED"

    # 3. Patch status to RESOLVED
    patch_res2 = client.patch(f"/api/v1/alerts/{alert_id}", json={"status": "RESOLVED"})
    assert patch_res2.status_code == 200
    assert patch_res2.json()["status"] == "RESOLVED"
