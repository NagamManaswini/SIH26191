"""Tests for AI Disaster Management Assistant Feature."""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_ai_assistant_chat_valid_query():
    """Test AI assistant chat endpoint with valid disaster query."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "Which shelters have available capacity?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "disclaimer" in data
    assert len(data["sources"]) > 0
    assert "AI-generated recommendations" in data["disclaimer"]


def test_ai_assistant_chat_red_zone_query():
    """Test AI assistant querying Red Zone status."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What areas are currently in the Red Zone?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Red Zone" in data["answer"] or "Hazard" in data["answer"]


def test_ai_assistant_chat_empty_query():
    """Test AI assistant with empty message validation."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "   "},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_ai_assistant_chat_flood_safety_query():
    """Test AI assistant responding to flood safety inquiry."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What should I do during a severe flood?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Flood" in data["answer"] or "Water" in data["answer"]
    assert "flood_response" in data["related_data"] or len(data["sources"]) > 0


def test_ai_assistant_chat_first_aid_query():
    """Test AI assistant responding to first aid medical inquiry."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "How do I give first aid for hypothermia or bleeding?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "First Aid" in data["answer"] or "Medical" in data["answer"]
    assert "108" in data["answer"] or "Ambulance" in data["answer"]


def test_ai_assistant_chat_dijkstra_routing_query():
    """Test AI assistant explaining Dijkstra evacuation routing."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "How does Dijkstra route optimization work?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Dijkstra" in data["answer"] or "Routing" in data["answer"]

