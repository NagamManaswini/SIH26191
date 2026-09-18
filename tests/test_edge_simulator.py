import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_edge_overview_api():
    response = client.get("/api/edge/overview")
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data
    assert "SOFTWARE SIMULATION" in data["disclaimer"]
    assert "total_nodes" in data
    assert data["total_nodes"] >= 5
    assert "total_gateways" in data
    assert data["total_gateways"] >= 3
    assert "nodes" in data
    assert "gateways" in data
    
    first_node = data["nodes"][0]
    assert "node_id" in first_node
    assert "battery" in first_node
    assert "signal" in first_node
    assert "connected" in first_node
    assert "local_risk_score" in first_node
    assert "local_threshold" in first_node
    assert "siren_status" in first_node

def test_edge_simulate_network_failure_and_offline_actuation():
    # 1. Simulate network failure
    res_fail = client.post("/api/edge/simulate-failure")
    assert res_fail.status_code == 200
    fail_data = res_fail.json()
    assert fail_data["network_online"] is False
    assert fail_data["status"] == "SIMULATION_NETWORK_FAILED"

    # Verify overview reflects offline status
    res_ov = client.get("/api/edge/overview")
    assert res_ov.json()["network_online"] is False
    assert res_ov.json()["connected_nodes"] == 0

    # 2. Trigger severe hazard on offline node NODE-RN-001
    res_hazard = client.post("/api/edge/nodes/NODE-RN-001/trigger-hazard")
    assert res_hazard.status_code == 200
    hazard_data = res_hazard.json()
    assert hazard_data["siren_active"] is True
    assert hazard_data["local_risk_score"] >= hazard_data["local_threshold"]
    assert hazard_data["stored_in_offline_buffer"] is True
    assert hazard_data["current_offline_buffer_count"] >= 1

    # 3. Restore network and verify replay sync
    res_restore = client.post("/api/edge/restore-network")
    assert res_restore.status_code == 200
    restore_data = res_restore.json()
    assert restore_data["network_online"] is True
    assert restore_data["total_events_synced"] >= 1

    # 4. Verify nodes reconnected and queue flushed
    res_ov_restored = client.get("/api/edge/overview")
    assert res_ov_restored.json()["network_online"] is True
    assert res_ov_restored.json()["total_offline_queued_events"] == 0
    assert len(res_ov_restored.json()["recent_sync_logs"]) >= 1
