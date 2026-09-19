from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommunicationMessageCreate(BaseModel):
    category: str = Field(..., description="GENERAL, EVACUATION, ANIMAL_SAFETY, SHELTER, ROAD_BLOCK, WEATHER, EMERGENCY")
    title: str = Field(..., description="Message subject title")
    message: str = Field(..., description="Detailed message content")
    target_area: str = Field(default="ALL", description="Geographic sector or area")
    severity: str = Field(default="INFO", description="INFO, WARNING, HIGH, CRITICAL")
    sender_name: str = Field(default="Disaster Management Command")
    sender_role: str = Field(default="admin")
    is_emergency_broadcast: bool = Field(default=False)
    expiry_time: Optional[datetime] = None


class EmergencyBroadcastRequest(BaseModel):
    title: str = Field(..., description="Emergency broadcast title")
    message: str = Field(..., description="Broadcast body")
    target_area: str = Field(default="Chooralmala & Mundakkai")
    category: str = Field(default="EMERGENCY")
    severity: str = Field(default="CRITICAL")


class CommunicationMessageResponse(BaseModel):
    id: int
    category: str
    title: str
    message: str
    target_area: str
    severity: str
    sender_name: str
    sender_role: str
    is_emergency_broadcast: bool
    acknowledged_count: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
