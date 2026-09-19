"""Test Hazard Zone CRUD endpoints."""


def test_create_and_read_hazard_zone(client):
    payload = {
        "name": "North Hill Slope Landslide Zone",
        "hazard_type": "landslide",
        "risk_level": "RED",
        "risk_score": 0.92,
        "coordinates": [
            [
                [72.870, 19.070],
                [72.880, 19.070],
                [72.880, 19.080],
                [72.870, 19.080],
                [72.870, 19.070],
            ]
        ],
    }

    # 1. Create hazard zone
    response = client.post("/api/v1/hazards", json=payload)
    assert response.status_code == 201
    created_data = response.json()
    hazard_id = created_data["id"]
    assert created_data["name"] == payload["name"]
    assert created_data["risk_level"] == "RED"
    assert created_data["risk_score"] == 0.92
    assert len(created_data["coordinates"]) == 1

    # 2. Get by ID
    response = client.get(f"/api/v1/hazards/{hazard_id}")
    assert response.status_code == 200
    fetched_data = response.json()
    assert fetched_data["id"] == hazard_id

    # 3. List with risk_level filter
    response = client.get("/api/v1/hazards?risk_level=RED")
    assert response.status_code == 200
    hazards_list = response.json()
    assert len(hazards_list) >= 1
    assert all(h["risk_level"] == "RED" for h in hazards_list)


def test_update_hazard_zone(client):
    payload = {
        "name": "River Catchment Flood Buffer",
        "hazard_type": "flood",
        "risk_level": "YELLOW",
        "risk_score": 0.55,
        "coordinates": [
            [
                [72.850, 19.050],
                [72.860, 19.050],
                [72.860, 19.060],
                [72.850, 19.060],
                [72.850, 19.050],
            ]
        ],
    }
    create_res = client.post("/api/v1/hazards", json=payload)
    hazard_id = create_res.json()["id"]

    update_payload = {
        "risk_level": "RED",
        "risk_score": 0.88,
    }
    update_res = client.put(f"/api/v1/hazards/{hazard_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["risk_level"] == "RED"
    assert updated_data["risk_score"] == 0.88


def test_hazard_zone_not_found(client):
    response = client.get("/api/v1/hazards/999999")
    assert response.status_code == 404


def test_delete_hazard_zone(client):
    payload = {
        "name": "Temporary Erosion Zone",
        "hazard_type": "erosion",
        "risk_level": "GREEN",
        "risk_score": 0.20,
        "coordinates": [
            [
                [72.800, 19.000],
                [72.810, 19.000],
                [72.810, 19.010],
                [72.800, 19.010],
                [72.800, 19.000],
            ]
        ],
    }
    create_res = client.post("/api/v1/hazards", json=payload)
    hazard_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/hazards/{hazard_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/api/v1/hazards/{hazard_id}")
    assert get_res.status_code == 404
