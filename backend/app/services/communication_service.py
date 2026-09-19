"""Community Communication Service.

Handles community messages, official announcements, emergency broadcasts, area-specific targeting,
and notification abstraction layer dispatching.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.entities import CommunicationMessage
from backend.app.schemas.communication import CommunicationMessageCreate, EmergencyBroadcastRequest
from backend.app.services.notifications.abstract_notifier import notification_manager


def get_all_messages(
    db: Session,
    category: Optional[str] = None,
    target_area: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
) -> List[CommunicationMessage]:
    """Retrieve community communication messages filtered by category, target area, or severity."""
    query = db.query(CommunicationMessage)

    if category:
        query = query.filter(CommunicationMessage.category == category.upper())
    if severity:
        query = query.filter(CommunicationMessage.severity == severity.upper())
    if target_area and target_area.upper() != "ALL":
        query = query.filter(
            (CommunicationMessage.target_area.ilike(f"%{target_area}%")) | (CommunicationMessage.target_area == "ALL")
        )

    return query.order_by(CommunicationMessage.created_at.desc()).limit(limit).all()


def create_message(db: Session, msg_in: CommunicationMessageCreate) -> CommunicationMessage:
    """Create a new community communication message."""
    msg_obj = CommunicationMessage(
        category=msg_in.category.upper(),
        title=msg_in.title,
        message=msg_in.message,
        target_area=msg_in.target_area,
        severity=msg_in.severity.upper(),
        sender_name=msg_in.sender_name,
        sender_role=msg_in.sender_role,
        is_emergency_broadcast=msg_in.is_emergency_broadcast,
        expiry_time=msg_in.expiry_time,
    )
    db.add(msg_obj)
    db.commit()
    db.refresh(msg_obj)
    return msg_obj


def send_emergency_broadcast(db: Session, broadcast_in: EmergencyBroadcastRequest) -> Dict[str, Any]:
    """Sends an emergency broadcast message to a target geographic area across all communication channels."""
    msg_obj = CommunicationMessage(
        category=broadcast_in.category.upper(),
        title=f"EMERGENCY BROADCAST: {broadcast_in.title}",
        message=broadcast_in.message,
        target_area=broadcast_in.target_area,
        severity=broadcast_in.severity.upper(),
        sender_name="Disaster Management Command Center",
        sender_role="admin",
        is_emergency_broadcast=True,
    )
    db.add(msg_obj)
    db.commit()
    db.refresh(msg_obj)

    # Dispatch via Notification Abstraction Layer
    broadcast_dispatch = notification_manager.broadcast_emergency_message(
        target_area=broadcast_in.target_area,
        title=msg_obj.title,
        message=msg_obj.message,
        payload={"message_id": msg_obj.id, "severity": msg_obj.severity},
    )

    return {
        "broadcast_id": msg_obj.id,
        "title": msg_obj.title,
        "message": msg_obj.message,
        "target_area": msg_obj.target_area,
        "severity": msg_obj.severity,
        "created_at": msg_obj.created_at,
        "dispatch_details": broadcast_dispatch,
    }
