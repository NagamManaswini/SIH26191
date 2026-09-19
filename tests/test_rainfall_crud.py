"""Test Rainfall Records CRUD endpoints."""


def test_create_and_read_rainfall(client):
    payload = {
        "location_name": "Rain Gauge Station Beta - Western Hills",
        "rainfall_mm": 210.5,
        "duration_hours": 12.0,
        "intensity": "extreme",
        "latitude": 19.1200,
        "longitude": 72.9500,
    }

    # 1. Create
    res = client.post("/api/v1/rainfall-records", json=payload)
    assert res.status_code == 201
    rain_data = res.json()
    record_id = rain_data["id"]
    assert rain_data["location_name"] == payload["location_name"]
    assert rain_data["rainfall_mm"] == 210.5
    assert rain_data["intensity"] == "extreme"

    # 2. Get by ID
    get_res = client.get(f"/api/v1/rainfall-records/{record_id}")
    assert get_res.status_code == 200
    assert get_res.json()["latitude"] == payload["latitude"]

    # 3. List
    list_res = client.get("/api/v1/rainfall-records")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_delete_rainfall(client):
    payload = {
        "location_name": "Test Gauge Delta",
        "rainfall_mm": 45.0,
        "duration_hours": 6.0,
        "intensity": "moderate",
    }
    create_res = client.post("/api/v1/rainfall-records", json=payload)
    record_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/rainfall-records/{record_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/api/v1/rainfall-records/{record_id}")
    assert get_res.status_code == 404
