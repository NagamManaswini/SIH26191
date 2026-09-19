"""Tests for Animal Safety & Animal Shelters Module."""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


import uuid

def test_animal_crud_and_shelters():
    """Test animal registration, animal shelters, and rescue plan generation."""
    unique_tag = f"TEST-CATTLE-{uuid.uuid4().hex[:6].upper()}"
    # 1. Register Animal
    an_res = client.post(
        "/api/v1/animals",
        json={
            "tag_id": unique_tag,
            "owner_name": "Test Farm",
            "animal_type": "cattle",
            "name": "Dairy Herd",
            "location_name": "Red Zone Alpha",
            "emergency_status": "AT_RISK",
        },
    )
    assert an_res.status_code == 201
    an_data = an_res.json()
    assert an_data["tag_id"] == unique_tag


    # 2. Get Animal Shelters
    ans_res = client.get("/api/v1/animals/shelters")
    assert ans_res.status_code == 200
    ans_list = ans_res.json()
    assert isinstance(ans_list, list)

    # 3. Generate Rescue Plan
    plan_res = client.post("/api/v1/animals/rescue-plan")
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert "total_animals_at_risk" in plan_data
    assert "assignments" in plan_data
