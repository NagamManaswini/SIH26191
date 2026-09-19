"""Alert Service Layer for CRUD operations and Notification Dispatching."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.entities import Alert
from backend.app.schemas.alert import AlertCreate, AlertUpdate
from backend.app.services.notifications import notification_dispatcher


def get_all_alerts(
    db: Session,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    affected_area: Optional[str] = None,
    limit: int = 100,
) -> List[Alert]:
    """Retrieve alerts filtered by severity, status, or affected area."""
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity.upper())
    if status:
        query = query.filter(Alert.status == status.upper())
    if affected_area:
        query = query.filter(Alert.affected_area.ilike(f"%{affected_area}%"))

    return query.order_by(Alert.created_time.desc()).limit(limit).all()


def get_alert_by_id(db: Session, alert_id: int) -> Optional[Alert]:
    """Retrieve alert by primary key ID."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def create_alert(db: Session, alert_in: AlertCreate) -> Dict[str, Any]:
    """Create alert in DB and dispatch via Notification Providers."""
    severity = alert_in.severity.upper()
    if severity not in ["INFO", "WARNING", "HIGH", "CRITICAL"]:
        severity = "INFO"

    status_val = alert_in.status.upper()
    if status_val not in ["ACTIVE", "ACKNOWLEDGED", "RESOLVED", "EXPIRED"]:
        status_val = "ACTIVE"

    alert_obj = Alert(
        title=alert_in.title,
        message=alert_in.message,
        severity=severity,
        affected_area=alert_in.affected_area,
        recommended_action=alert_in.recommended_action,
        status=status_val,
    )
    db.add(alert_obj)
    db.commit()
    db.refresh(alert_obj)

    # Convert alert to dict and dispatch notifications
    alert_dict = {
        "id": alert_obj.id,
        "title": alert_obj.title,
        "message": alert_obj.message,
        "severity": alert_obj.severity,
        "affected_area": alert_obj.affected_area,
        "recommended_action": alert_obj.recommended_action,
        "status": alert_obj.status,
    }
    dispatches = notification_dispatcher.dispatch_alert_notifications(alert_dict)

    res = {
        "id": alert_obj.id,
        "title": alert_obj.title,
        "message": alert_obj.message,
        "severity": alert_obj.severity,
        "affected_area": alert_obj.affected_area,
        "recommended_action": alert_obj.recommended_action,
        "status": alert_obj.status,
        "created_time": alert_obj.created_time,
        "updated_at": alert_obj.updated_at,
        "notification_dispatches": dispatches,
    }
    return res


def update_alert(db: Session, alert_id: int, alert_in: AlertUpdate) -> Optional[Alert]:
    """Update alert fields such as status, severity, or recommended action."""
    alert_obj = get_alert_by_id(db, alert_id)
    if not alert_obj:
        return None

    if alert_in.status:
        st = alert_in.status.upper()
        if st in ["ACTIVE", "ACKNOWLEDGED", "RESOLVED", "EXPIRED"]:
            alert_obj.status = st
    if alert_in.severity:
        sev = alert_in.severity.upper()
        if sev in ["INFO", "WARNING", "HIGH", "CRITICAL"]:
            alert_obj.severity = sev
    if alert_in.title:
        alert_obj.title = alert_in.title
    if alert_in.message:
        alert_obj.message = alert_in.message
    if alert_in.recommended_action is not None:
        alert_obj.recommended_action = alert_in.recommended_action

    db.commit()
    db.refresh(alert_obj)
    return alert_obj


def log_alert_action(db: Session, alert_id: Optional[int], action: str, performed_by: str, details: str) -> AlertAuditLog:
    """Log an audit entry for alert actions."""
    from backend.app.models.entities import AlertAuditLog
    audit_entry = AlertAuditLog(
        alert_id=alert_id,
        action=action,
        performed_by=performed_by,
        details=details,
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry


def trigger_manual_sos(
    db: Session,
    affected_area: str,
    title: str,
    message: str,
    recommended_action: str,
    performed_by: str = "Admin Command",
) -> Dict[str, Any]:
    """Manually trigger a CRITICAL emergency SOS sound alert across active systems."""
    alert_obj = Alert(
        title=f"MANUAL SOS: {title}",
        message=message,
        severity="CRITICAL",
        affected_area=affected_area,
        recommended_action=recommended_action,
        status="ACTIVE",
    )
    db.add(alert_obj)
    db.commit()
    db.refresh(alert_obj)

    log_alert_action(
        db=db,
        alert_id=alert_obj.id,
        action="MANUAL_SOS_TRIGGERED",
        performed_by=performed_by,
        details=f"Manual SOS triggered for {affected_area}: {title}",
    )

    return {
        "status": "SOS_ACTIVE",
        "alert_id": alert_obj.id,
        "title": alert_obj.title,
        "message": alert_obj.message,
        "severity": "CRITICAL",
        "affected_area": affected_area,
        "recommended_action": recommended_action,
        "sos_sound_required": True,
        "timestamp": alert_obj.created_time,
    }


def stop_manual_sos(db: Session, alert_id: int, performed_by: str = "Admin Command") -> Dict[str, Any]:
    """Deactivate an active CRITICAL SOS alert."""
    alert_obj = get_alert_by_id(db, alert_id)
    if alert_obj:
        alert_obj.status = "RESOLVED"
        db.commit()

    log_alert_action(
        db=db,
        alert_id=alert_id,
        action="SOS_STOPPED",
        performed_by=performed_by,
        details=f"Emergency SOS alert ID {alert_id} deactivated by user.",
    )

    return {"status": "SOS_STOPPED", "alert_id": alert_id}


def get_audit_logs(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch audit logs for emergency alert history."""
    from backend.app.models.entities import AlertAuditLog
    logs = db.query(AlertAuditLog).order_by(AlertAuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "alert_id": l.alert_id,
            "action": l.action,
            "performed_by": l.performed_by,
            "details": l.details,
            "timestamp": l.timestamp,
        }
        for l in logs
    ]

