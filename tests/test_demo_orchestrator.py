import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_demo_status():
    response = client.get("/api/demo/status")
    assert response.status_code == 200
    data = response.json()
    assert "current_stage" in data
    assert "total_stages" in data
    assert data["total_stages"] == 15
    assert "stage_info" in data
    assert "stage_title" in data["stage_info"]
    assert "risk_level" in data["stage_info"]

def test_demo_start_and_advance():
    response = client.post("/api/demo/start", json={"auto_play": False, "jump_to_stage": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["current_stage"] == 5
    assert data["stage_info"]["stage_number"] == 5

    # Advance stage
    response_adv = client.post("/api/demo/advance-step")
    assert response_adv.status_code == 200
    data_adv = response_adv.json()
    assert data_adv["current_stage"] == 6

    # Stop demo
    response_stop = client.post("/api/demo/stop")
    assert response_stop.status_code == 200
    data_stop = response_stop.json()
    assert data_stop["current_stage"] == 1
    assert data_stop["is_running"] is False
