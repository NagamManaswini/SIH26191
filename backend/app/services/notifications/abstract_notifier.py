"""Notification Abstraction Layer for Future System Integrations.

Provides clean interfaces for future SMS providers, Push Notifications, Email,
and Government Emergency Communication Networks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseNotificationProvider(ABC):
    """Abstract base class for notification channels."""

    @abstractmethod
    def send_notification(self, recipient: str, title: str, message: str, payload: Dict[str, Any]) -> bool:
        pass


class MockSMSNotificationProvider(BaseNotificationProvider):
    """Mock SMS provider abstraction for future SMS gateway integration."""

    def send_notification(self, recipient: str, title: str, message: str, payload: Dict[str, Any]) -> bool:
        print(f"[SMS Provider Abstraction] Dispatching SMS to {recipient}: '{title}' — {message[:50]}...")
        return True


class MockPushNotificationProvider(BaseNotificationProvider):
    """Mock Web/Mobile Push notification provider abstraction."""

    def send_notification(self, recipient: str, title: str, message: str, payload: Dict[str, Any]) -> bool:
        print(f"[Push Provider Abstraction] Sending Push Notification to target '{recipient}': '{title}'")
        return True


class MockGovSystemProvider(BaseNotificationProvider):
    """Mock Government Emergency Network integration provider."""

    def send_notification(self, recipient: str, title: str, message: str, payload: Dict[str, Any]) -> bool:
        print(f"[Gov Emergency Net] Transmitting broadcast packet to government sector '{recipient}': '{title}'")
        return True


class NotificationManager:
    """Manages active notification dispatching channels."""

    def __init__(self):
        self.providers: List[BaseNotificationProvider] = [
            MockSMSNotificationProvider(),
            MockPushNotificationProvider(),
            MockGovSystemProvider(),
        ]

    def broadcast_emergency_message(self, target_area: str, title: str, message: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        for provider in self.providers:
            success = provider.send_notification(recipient=target_area, title=title, message=message, payload=payload)
            results.append({"provider": provider.__class__.__name__, "success": success})

        return {
            "target_area": target_area,
            "title": title,
            "dispatches": results,
            "total_channels": len(results),
        }


notification_manager = NotificationManager()
