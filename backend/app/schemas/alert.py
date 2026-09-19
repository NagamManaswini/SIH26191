"""Pydantic request/response schemas for Alert Management System."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AlertCreate(BaseModel):
    title: str = Field(..., description="Alert headline title", min_length=3, max_length=255)
    message: str = Field(..., description="Detailed alert message and advisory text")
    severity: str = Field("INFO", description="Alert severity level: INFO, WARNING, HIGH, CRITICAL")
    affected_area: str = Field("General District", description="Name of affected spatial area")
    recommended_action: Optional[str] = Field("Monitor emergency broadcasts.", description="Recommended safety action for citizens")
    status: str = Field("ACTIVE", description="Alert status: ACTIVE, ACKNOWLEDGED, RESOLVED, EXPIRED")


class AlertUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Updated status: ACTIVE, ACKNOWLEDGED, RESOLVED, EXPIRED")
    title: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = None
    severity: Optional[str] = Field(None, description="INFO, WARNING, HIGH, CRITICAL")
    recommended_action: Optional[str] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    message: str
    severity: str
    affected_area: str
    recommended_action: Optional[str] = None
    status: str
    created_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    notification_dispatches: Optional[List[Dict[str, Any]]] = None
