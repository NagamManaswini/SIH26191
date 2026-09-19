"""FastAPI Router for Community Communication Web App."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.communication import (
    CommunicationMessageCreate,
    CommunicationMessageResponse,
    EmergencyBroadcastRequest,
)
from backend.app.services.communication_service import (
    get_all_messages,
    create_message,
    send_emergency_broadcast,
)

router = APIRouter(prefix="/communications", tags=["Community Communication"])


@router.get("/messages", response_model=List[CommunicationMessageResponse], summary="List community messages")
def list_messages(
    category: Optional[str] = None,
    target_area: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve community messages filtered by category (EVACUATION, ANIMAL_SAFETY, WEATHER, etc.), target area, or severity."""
    return get_all_messages(db, category=category, target_area=target_area, severity=severity)


@router.post("/messages", response_model=CommunicationMessageResponse, status_code=status.HTTP_201_CREATED, summary="Post community message")
def post_message(msg_in: CommunicationMessageCreate, db: Session = Depends(get_db)):
    """Post an official community announcement or operational update."""
    return create_message(db, msg_in)


@router.post("/emergency-broadcast", summary="Send emergency broadcast")
def emergency_broadcast(broadcast_in: EmergencyBroadcastRequest, db: Session = Depends(get_db)):
    """Dispatch emergency broadcast to specified geographic area across notification channels."""
    return send_emergency_broadcast(db, broadcast_in)
