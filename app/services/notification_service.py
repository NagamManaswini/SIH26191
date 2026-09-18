"""
Notification Service Abstraction for Flash Flood Early Warning System.

Provides modular providers for emergency multi-channel alerting:
- SMSProvider (SMS gateway simulation)
- VoiceProvider (Automated IVR voice call simulation)
- PushProvider (Mobile and Web Push notification simulation)
- SirenProvider (Edge IoT siren relay & tone activation simulation)

Ready for future plug-and-play integrations with Twilio, FCM, AWS SNS, and LoRaWAN siren arrays.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
import logging

logger = logging.getLogger("notification_service")


class BaseNotificationProvider(ABC):
    """
    Abstract base provider interface for emergency notification dispatching.
    """
    def __init__(self, name: str, channel_type: str):
        self.name = name
        self.channel_type = channel_type

    @abstractmethod
    def send(
        self,
        recipient: str,
        title: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dispatches emergency notification to recipient/zone.
        Returns a delivery receipt dictionary.
        """
        pass


class SMSProvider(BaseNotificationProvider):
    """
    Simulated SMS Emergency Gateway Provider.
    Simulates cellular broadcast to local cell towers and registered emergency contacts.
    """
    def __init__(self):
        super().__init__(name="Telecom-SMS-Gateway", channel_type="SMS")

    def send(
        self,
        recipient: str,
        title: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        dispatch_id = f"SMS-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Format cellular broadcast payload
        payload_preview = f"[{severity}] {title}: {message}"
        
        logger.info(f"[SMS DISPATCH] ID={dispatch_id} To={recipient} | {payload_preview}")
        
        return {
            "dispatch_id": dispatch_id,
            "provider": self.name,
            "channel": self.channel_type,
            "recipient": recipient,
            "severity": severity,
            "title": title,
            "message": message,
            "status": "DELIVERED",
            "latency_ms": 142,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }


class VoiceProvider(BaseNotificationProvider):
    """
    Simulated Automated IVR Voice Telephony Provider.
    Simulates placing priority voice calls with text-to-speech sirens to nodal officers.
    """
    def __init__(self):
        super().__init__(name="Emergency-IVR-Voice-Engine", channel_type="VOICE_IVR")

    def send(
        self,
        recipient: str,
        title: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        dispatch_id = f"VOX-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        call_script = f"Urgent flash flood alert for {recipient}. Severity: {severity}. {message}. Take immediate precautionary action."
        
        logger.info(f"[VOICE CALL QUEUE] ID={dispatch_id} To={recipient} | Script: {call_script}")
        
        return {
            "dispatch_id": dispatch_id,
            "provider": self.name,
            "channel": self.channel_type,
            "recipient": recipient,
            "severity": severity,
            "title": title,
            "message": message,
            "script_spoken": call_script,
            "status": "CALL_CONNECTED",
            "call_duration_sec": 28,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }


class PushProvider(BaseNotificationProvider):
    """
    Simulated Mobile / Web Push Notification Provider.
    Simulates high-priority FCM / APNS payload with geo-fenced heads-up display.
    """
    def __init__(self):
        super().__init__(name="FCM-Push-Gateway", channel_type="PUSH")

    def send(
        self,
        recipient: str,
        title: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        dispatch_id = f"FCM-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"[PUSH BROADCAST] ID={dispatch_id} Topic={recipient} | {title}")
        
        return {
            "dispatch_id": dispatch_id,
            "provider": self.name,
            "channel": self.channel_type,
            "recipient": recipient,
            "severity": severity,
            "title": title,
            "message": message,
            "status": "PUSHED",
            "active_devices_reached": 1420,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }


class SirenProvider(BaseNotificationProvider):
    """
    Simulated Edge IoT Physical Siren Provider.
    Simulates LoRaWAN/4G telemetry command to trigger 110dB acoustic siren nodes in flash flood zones.
    """
    def __init__(self):
        super().__init__(name="Edge-Siren-Array-Relay", channel_type="SIREN")

    def send(
        self,
        recipient: str,
        title: str,
        message: str,
        severity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        dispatch_id = f"SRN-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Map severity to acoustic tone pattern
        tone_map = {
            "EMERGENCY": "CONTINUOUS_EVACUATION_WARBLE_110DB",
            "DANGER": "INTERMITTENT_HIGH_PITCH_100DB",
            "WARNING": "SHORT_CHIRP_BEACON_85DB",
            "INFO": "SILENT_STROBE_TEST"
        }
        tone = tone_map.get(severity, "INTERMITTENT_HIGH_PITCH_100DB")
        
        logger.info(f"[SIREN TRIGGER] ID={dispatch_id} Zone={recipient} | Tone={tone}")
        
        return {
            "dispatch_id": dispatch_id,
            "provider": self.name,
            "channel": self.channel_type,
            "recipient": recipient,
            "severity": severity,
            "title": title,
            "message": message,
            "tone_pattern": tone,
            "status": "SIREN_ACTIVATED",
            "siren_nodes_online": 6,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }


class NotificationService:
    """
    Unified Notification Service Orchestrator.
    Manages multi-channel dispatch, audit log history, and provider registry.
    """
    def __init__(self):
        self.providers: Dict[str, BaseNotificationProvider] = {
            "SMS": SMSProvider(),
            "VOICE": VoiceProvider(),
            "PUSH": PushProvider(),
            "SIREN": SirenProvider(),
        }
        # In-memory circular audit log (stores last 200 dispatches)
        self.audit_log: List[Dict[str, Any]] = []

    def dispatch_alert(
        self,
        alert_id: int,
        title: str,
        message: str,
        severity: str,
        affected_area: str,
        channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Dispatches alert across specified or all notification channels.
        """
        target_channels = channels or list(self.providers.keys())
        dispatched_receipts: List[Dict[str, Any]] = []
        
        meta = metadata or {}
        meta["alert_id"] = alert_id
        meta["affected_area"] = affected_area
        
        for ch in target_channels:
            provider = self.providers.get(ch.upper())
            if provider:
                receipt = provider.send(
                    recipient=affected_area,
                    title=title,
                    message=message,
                    severity=severity,
                    metadata=meta
                )
                dispatched_receipts.append(receipt)
                self.audit_log.insert(0, receipt)
        
        # Keep log size bounded
        if len(self.audit_log) > 200:
            self.audit_log = self.audit_log[:200]
            
        return dispatched_receipts

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns recent notification audit logs.
        """
        return self.audit_log[:limit]

    def clear_logs(self):
        self.audit_log.clear()


# Global singleton instance
notification_service = NotificationService()
