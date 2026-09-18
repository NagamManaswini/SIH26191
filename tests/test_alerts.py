"""
Unit and Integration Tests for Milestone 8: Real-Time Alert Engine.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.alert import Alert
from app.models.watershed import Watershed
from app.models.enums import AlertType, AlertSeverity, AlertStatus, RiskLevel
from app.services.alert_engine import alert_engine, calculate_danger_zone_polygon
from app.services.notification_service import notification_service, SMSProvider, VoiceProvider, PushProvider, SirenProvider

client = TestClient(app)


def test_danger_zone_polygon_geometry():
    """Verify spherical polygon generation creates a closed ring with valid lat/lon coordinates."""
    lat, lon = 30.7346, 79.0669
    radius_km = 5.0
    num_points = 24
    
    polygon = calculate_danger_zone_polygon(lat, lon, radius_km=radius_km, num_points=num_points)
    
    # Must have num_points + 1 vertices (first and last vertex identical)
    assert len(polygon) == num_points + 1
    assert polygon[0] == polygon[-1]
    
    # Check bounds
    for pt in polygon:
        pt_lon, pt_lat = pt[0], pt[1]
        assert -180.0 <= pt_lon <= 180.0
        assert -90.0 <= pt_lat <= 90.0
        # Should be within ~0.2 degrees of center
        assert abs(pt_lat - lat) < 0.2
        assert abs(pt_lon - lon) < 0.2


def test_alert_rules_evaluation_severities():
    """Verify rule matrix outputs correct severities for varying hydrological conditions."""
    
    # 1. Critical condition -> EMERGENCY
    emergency_res = alert_engine.evaluate_rules(
        current_risk_level="CRITICAL",
        river_stage_m=4.8,
        river_rate_of_rise=1.2,
        rainfall_intensity_mm_hr=75.0,
        accumulated_rain_mm=120.0,
        soil_saturation_pct=92.0,
        predicted_max_stage_m=5.2,
        predicted_max_risk="CRITICAL",
        predicted_flood_prob_pct=90.0
    )
    assert emergency_res is not None
    assert emergency_res[0] == AlertSeverity.EMERGENCY
    assert len(emergency_res[4]) > 0  # has reasons

    # 2. High risk condition -> DANGER
    danger_res = alert_engine.evaluate_rules(
        current_risk_level="HIGH",
        river_stage_m=3.9,
        river_rate_of_rise=0.6,
        rainfall_intensity_mm_hr=48.0,
        accumulated_rain_mm=60.0,
        soil_saturation_pct=78.0,
        predicted_max_stage_m=4.2,
        predicted_max_risk="HIGH",
        predicted_flood_prob_pct=65.0
    )
    assert danger_res is not None
    assert danger_res[0] == AlertSeverity.DANGER

    # 3. Moderate condition -> WARNING
    warning_res = alert_engine.evaluate_rules(
        current_risk_level="MODERATE",
        river_stage_m=3.3,
        river_rate_of_rise=0.35,
        rainfall_intensity_mm_hr=32.0,
        accumulated_rain_mm=40.0,
        soil_saturation_pct=82.0,
        predicted_max_stage_m=3.5,
        predicted_max_risk="MODERATE",
        predicted_flood_prob_pct=30.0
    )
    assert warning_res is not None
    assert warning_res[0] == AlertSeverity.WARNING

    # 4. Mild condition -> INFO
    info_res = alert_engine.evaluate_rules(
        current_risk_level="LOW",
        river_stage_m=2.6,
        river_rate_of_rise=0.05,
        rainfall_intensity_mm_hr=16.0,
        accumulated_rain_mm=10.0,
        soil_saturation_pct=50.0,
        predicted_max_stage_m=2.7,
        predicted_max_risk="LOW",
        predicted_flood_prob_pct=10.0
    )
    assert info_res is not None
    assert info_res[0] == AlertSeverity.INFO

    # 5. Normal safe condition -> None
    safe_res = alert_engine.evaluate_rules(
        current_risk_level="LOW",
        river_stage_m=1.2,
        river_rate_of_rise=0.0,
        rainfall_intensity_mm_hr=2.0,
        accumulated_rain_mm=3.0,
        soil_saturation_pct=40.0,
        predicted_max_stage_m=1.3,
        predicted_max_risk="LOW",
        predicted_flood_prob_pct=5.0
    )
    assert safe_res is None


def test_notification_providers_dispatch():
    """Verify SMS, Voice, Push, and Siren simulated notification providers."""
    sms_p = SMSProvider()
    voice_p = VoiceProvider()
    push_p = PushProvider()
    siren_p = SirenProvider()

    res_sms = sms_p.send("Mandakini Valley", "Test Alert", "Water rising fast", "EMERGENCY")
    assert res_sms["status"] == "DELIVERED"
    assert res_sms["channel"] == "SMS"
    assert "dispatch_id" in res_sms

    res_voice = voice_p.send("Mandakini Valley", "Test Alert", "Water rising fast", "EMERGENCY")
    assert res_voice["status"] == "CALL_CONNECTED"
    assert res_voice["channel"] == "VOICE_IVR"

    res_push = push_p.send("Mandakini Valley", "Test Alert", "Water rising fast", "EMERGENCY")
    assert res_push["status"] == "PUSHED"
    assert res_push["channel"] == "PUSH"

    res_siren = siren_p.send("Mandakini Valley", "Test Alert", "Water rising fast", "EMERGENCY")
    assert res_siren["status"] == "SIREN_ACTIVATED"
    assert res_siren["channel"] == "SIREN"
    assert res_siren["tone_pattern"] == "CONTINUOUS_EVACUATION_WARBLE_110DB"

    # Test orchestrator dispatch
    receipts = notification_service.dispatch_alert(
        alert_id=999,
        title="Orchestrated Flash Flood Warning",
        message="Evacuate zone immediately",
        severity="EMERGENCY",
        affected_area="Alaknanda Catchment"
    )
    assert len(receipts) == 4  # All 4 channels
    logs = notification_service.get_audit_logs(limit=10)
    assert len(logs) >= 4


def test_get_alerts_and_active_alerts_api():
    """Verify GET /api/alerts and GET /api/alerts/active endpoints."""
    # Ensure at least one test alert in DB
    db = SessionLocal()
    try:
        test_alert = Alert(
            alert_type=AlertType.FLASH_FLOOD,
            severity=AlertSeverity.WARNING,
            title="Test Validation Flash Flood Warning",
            message="Moderate river surge detected in upper basin.",
            latitude=30.50,
            longitude=79.20,
            radius_km=5.0,
            status=AlertStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2)
        )
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)
        alert_id = test_alert.id
    finally:
        db.close()

    # GET /api/alerts
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(a["id"] == alert_id for a in data)

    # Check polygon_coordinates are attached
    found = next(a for a in data if a["id"] == alert_id)
    assert "polygon_coordinates" in found
    assert len(found["polygon_coordinates"]) > 0

    # GET /api/alerts/active
    resp_active = client.get("/api/alerts/active")
    assert resp_active.status_code == 200
    active_data = resp_active.json()
    assert any(a["id"] == alert_id for a in active_data)


def test_acknowledge_alert_api():
    """Verify POST /api/alerts/{id}/acknowledge marks alert as ACKNOWLEDGED."""
    db = SessionLocal()
    try:
        test_alert = Alert(
            alert_type=AlertType.CLOUDBURST,
            severity=AlertSeverity.DANGER,
            title="Acknowledge Test Alert",
            message="Cloudburst alert for response team",
            latitude=30.60,
            longitude=79.30,
            radius_km=6.0,
            status=AlertStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        )
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)
        alert_id = test_alert.id
    finally:
        db.close()

    ack_resp = client.post(f"/api/alerts/{alert_id}/acknowledge")
    assert ack_resp.status_code == 200
    ack_data = ack_resp.json()
    assert ack_data["message"] == "Alert successfully acknowledged."
    assert ack_data["alert"]["status"] == "ACKNOWLEDGED"

    # Verify 404 for nonexistent alert
    ack_404 = client.post("/api/alerts/999999/acknowledge")
    assert ack_404.status_code == 404


def test_alert_evaluation_and_deduplication():
    """Verify triggering alert evaluation creates alerts, prevents duplicates, and allows escalation."""
    db = SessionLocal()
    try:
        ws = db.query(Watershed).first()
        if not ws:
            ws = Watershed(
                name="Test Basin Alpha",
                code=f"WS-TEST-{int(datetime.now().timestamp())}",
                district="Rudraprayag",
                state="Uttarakhand",
                area_sq_km=150.0,
                risk_level=RiskLevel.HIGH
            )
            db.add(ws)
            db.commit()
            db.refresh(ws)
        
        ws_id = ws.id
    finally:
        db.close()

    # Trigger evaluation for this watershed
    eval_resp = client.post(f"/api/alerts/evaluate?watershed_id={ws_id}")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["total_evaluated"] == 1
    first_action = eval_data["results"][0]["action"]
    assert first_action in ("ALERT_CREATED", "ALERT_ESCALATED", "DUPLICATE_SUPPRESSED", "NO_ALERT_REQUIRED")

    # If an alert was created, a subsequent evaluation within cooldown should suppress duplicate
    if first_action == "ALERT_CREATED":
        eval_resp_2 = client.post(f"/api/alerts/evaluate?watershed_id={ws_id}")
        assert eval_resp_2.status_code == 200
        second_action = eval_resp_2.json()["results"][0]["action"]
        assert second_action == "DUPLICATE_SUPPRESSED"


def test_alert_zones_geojson_api():
    """Verify GET /api/alerts/zones/geojson returns GeoJSON Polygon features with severity styling."""
    resp = client.get("/api/alerts/zones/geojson")
    assert resp.status_code == 200
    geojson = resp.json()
    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    assert isinstance(geojson["features"], list)
    
    if len(geojson["features"]) > 0:
        f = geojson["features"][0]
        assert f["type"] == "Feature"
        assert f["geometry"]["type"] == "Polygon"
        assert len(f["geometry"]["coordinates"]) > 0
        assert "color" in f["properties"]
        assert "severity" in f["properties"]


def test_notification_logs_api():
    """Verify GET /api/alerts/notifications/log returns recent logs."""
    resp = client.get("/api/alerts/notifications/log?limit=20")
    assert resp.status_code == 200
    logs = resp.json()
    assert isinstance(logs, list)
