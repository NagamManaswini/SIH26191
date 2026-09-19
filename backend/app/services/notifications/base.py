"""Base interface for Notification Providers Abstraction Layer."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseNotificationProvider(ABC):
    """Abstract base class for notification providers (SMS, Push, Email, Dashboard)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the notification provider."""
        pass

    @abstractmethod
    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch notification alert payload.

        Args:
            alert_data: Dictionary containing title, message, severity, affected_area,
                        recommended_action, and status.

        Returns:
            Dictionary with status, provider_name, and delivery_meta.
        """
        pass
