"""Automated unit test suite for Alert Management System CRUD & Notification Dispatcher."""

from backend.app.models.entities import Alert
from backend.app.schemas.alert import AlertCreate, AlertUpdate
from backend.app.services.alert_service import (
    create_alert,
    get_all_alerts,
    get_alert_by_id,
    update_alert,
)
from backend.app.services.notifications import notification_dispatcher


def test_create_and_get_alert(db):
    """Verify alert creation and DB retrieval."""
    alert_in = AlertCreate(
        title="CRITICAL FLOOD WARNING",
        message="Riverside Sector A is experiencing sudden water level rise. Evacuate immediately.",
        severity="CRITICAL",
        affected_area="Riverside Sector A",
        recommended_action="Move to Central High School Relief Shelter immediately.",
        status="ACTIVE",
    )

    created = create_alert(db, alert_in)
    assert created["id"] is not None
    assert created["title"] == "CRITICAL FLOOD WARNING"
    assert created["severity"] == "CRITICAL"
    assert created["status"] == "ACTIVE"
    assert "notification_dispatches" in created
    assert len(created["notification_dispatches"]) > 0

    fetched = get_alert_by_id(db, created["id"])
    assert fetched is not None
    assert fetched.affected_area == "Riverside Sector A"


def test_update_alert_status(db):
    """Verify updating alert status to ACKNOWLEDGED or RESOLVED."""
    alert_in = AlertCreate(
        title="Landslide Warning",
        message="Steep Slope Highway landslide risk detected.",
        severity="HIGH",
        affected_area="Foothill Pass",
        recommended_action="Use North Detour.",
        status="ACTIVE",
    )
    created = create_alert(db, alert_in)

    # Patch status to ACKNOWLEDGED
    updated = update_alert(db, created["id"], AlertUpdate(status="ACKNOWLEDGED"))
    assert updated.status == "ACKNOWLEDGED"

    # Patch status to RESOLVED
    resolved = update_alert(db, created["id"], AlertUpdate(status="RESOLVED"))
    assert resolved.status == "RESOLVED"


def test_notification_dispatcher_channels():
    """Verify notification dispatcher selects appropriate providers based on severity."""
    info_dispatches = notification_dispatcher.dispatch_alert_notifications({
        "title": "Info Note",
        "severity": "INFO",
    })
    # INFO severity should trigger Web Provider only
    assert len(info_dispatches) == 1
    assert info_dispatches[0]["provider"] == "DashboardWeb"

    critical_dispatches = notification_dispatcher.dispatch_alert_notifications({
        "title": "Critical Flash Flood",
        "severity": "CRITICAL",
    })
    # CRITICAL severity should trigger Web, Email, Push, and SMS providers (4 providers)
    assert len(critical_dispatches) == 4
    provider_names = [d["provider"] for d in critical_dispatches]
    assert "DashboardWeb" in provider_names
    assert "Email" in provider_names
    assert "PushNotification" in provider_names
    assert "SMS" in provider_names
