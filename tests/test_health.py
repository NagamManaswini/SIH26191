"""Test GET /health API endpoint."""


def test_health_endpoint(client):
    """Test health endpoint returns 200 OK and valid health response payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_status"] == "connected"
    assert "version" in data
    assert "timestamp" in data
