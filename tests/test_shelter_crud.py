"""Test Shelter CRUD endpoints."""


def test_create_and_read_shelter(client):
    payload = {
        "name": "Community Hall Relief Center",
        "address": "42 Riverside Road, Zone 2",
        "capacity": 300,
        "current_occupancy": 45,
        "status": "active",
        "contact_number": "+91-9876543210",
        "latitude": 19.0760,
        "longitude": 72.8777,
    }

    # 1. Create shelter
    response = client.post("/api/v1/shelters", json=payload)
    assert response.status_code == 201
    created_data = response.json()
    shelter_id = created_data["id"]
    assert created_data["name"] == payload["name"]
    assert created_data["available_capacity"] == 300 - 45
    assert created_data["latitude"] == payload["latitude"]
    assert created_data["longitude"] == payload["longitude"]

    # 2. Get shelter by ID
    response = client.get(f"/api/v1/shelters/{shelter_id}")
    assert response.status_code == 200
    fetched_data = response.json()
    assert fetched_data["id"] == shelter_id
    assert fetched_data["capacity"] == 300

    # 3. List shelters
    response = client.get("/api/v1/shelters")
    assert response.status_code == 200
    shelters_list = response.json()
    assert len(shelters_list) >= 1
    assert any(s["id"] == shelter_id for s in shelters_list)


def test_update_shelter(client):
    payload = {
        "name": "Stadium Emergency Shelter",
        "capacity": 1000,
        "current_occupancy": 100,
        "latitude": 19.0800,
        "longitude": 72.8800,
    }
    create_res = client.post("/api/v1/shelters", json=payload)
    shelter_id = create_res.json()["id"]

    update_payload = {
        "current_occupancy": 450,
        "status": "active",
    }
    update_res = client.put(f"/api/v1/shelters/{shelter_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["current_occupancy"] == 450
    assert updated_data["available_capacity"] == 550


def test_shelter_validation_occupancy_exceeds_capacity(client):
    invalid_payload = {
        "name": "Small School Shelter",
        "capacity": 50,
        "current_occupancy": 100,  # Invalid: > capacity
        "latitude": 19.0500,
        "longitude": 72.8500,
    }
    response = client.post("/api/v1/shelters", json=invalid_payload)
    assert response.status_code == 400
    assert "occupancy cannot exceed" in response.json()["detail"]


def test_shelter_not_found(client):
    response = client.get("/api/v1/shelters/999999")
    assert response.status_code == 404


def test_delete_shelter(client):
    payload = {
        "name": "Temporary Tent Camp",
        "capacity": 200,
        "latitude": 19.1000,
        "longitude": 72.9000,
    }
    create_res = client.post("/api/v1/shelters", json=payload)
    shelter_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/shelters/{shelter_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/api/v1/shelters/{shelter_id}")
    assert get_res.status_code == 404
