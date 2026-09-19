"""Test Population CRUD endpoints."""


def test_create_and_read_population(client):
    payload = {
        "location_name": "District 1 Flood Plain Sector A",
        "total_population": 15000,
        "vulnerable_population": 2500,
        "density_per_sq_km": 5200.0,
    }

    # 1. Create
    res = client.post("/api/v1/population", json=payload)
    assert res.status_code == 201
    pop_data = res.json()
    pop_id = pop_data["id"]
    assert pop_data["location_name"] == payload["location_name"]
    assert pop_data["total_population"] == 15000

    # 2. Get by ID
    get_res = client.get(f"/api/v1/population/{pop_id}")
    assert get_res.status_code == 200
    assert get_res.json()["vulnerable_population"] == 2500

    # 3. List
    list_res = client.get("/api/v1/population")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_population_validation_vulnerable_exceeds_total(client):
    payload = {
        "location_name": "Invalid Sector",
        "total_population": 100,
        "vulnerable_population": 200,  # Invalid: > total
    }
    res = client.post("/api/v1/population", json=payload)
    assert res.status_code == 400
    assert "cannot exceed total population" in res.json()["detail"]


def test_delete_population(client):
    payload = {
        "location_name": "Temporary Shelter Settlement",
        "total_population": 500,
        "vulnerable_population": 50,
    }
    create_res = client.post("/api/v1/population", json=payload)
    pop_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/population/{pop_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/api/v1/population/{pop_id}")
    assert get_res.status_code == 404
