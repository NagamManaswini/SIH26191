"""Notification Providers Implementation for SIH26191.

Includes:
- DashboardWebNotificationProvider (active prototype provider)
- SMSNotificationProvider (stub for Twilio / AWS SNS integration)
- PushNotificationProvider (stub for Firebase FCM / APNs integration)
- EmailNotificationProvider (stub for SendGrid / Amazon SES integration)
- NotificationDispatcher (orchestrator)
"""

import datetime
from typing import Dict, Any, List
from backend.app.services.notifications.base import BaseNotificationProvider


class DashboardWebNotificationProvider(BaseNotificationProvider):
    """Local Web Dashboard Notification Provider (Active for Prototype)."""

    @property
    def provider_name(self) -> str:
        return "DashboardWeb"

    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch real-time notification to Web Dashboard event stream."""
        return {
            "provider": self.provider_name,
            "status": "DELIVERED",
            "channel": "web_dashboard_websocket",
            "delivered_at": datetime.datetime.now().isoformat(),
            "meta": {
                "title": alert_data.get("title"),
                "severity": alert_data.get("severity"),
                "affected_area": alert_data.get("affected_area"),
            },
        }


class SMSNotificationProvider(BaseNotificationProvider):
    """SMS Notification Provider Stub (Twilio / AWS SNS integration point)."""

    @property
    def provider_name(self) -> str:
        return "SMS"

    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock SMS dispatch for prototype without requiring paid API keys.

        Production Integration Notes:
        -----------------------------
        1. Install twilio or boto3 package: pip install twilio
        2. Set environment variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
        3. Call twilio_client.messages.create(to=recipient, from_=TWILIO_PHONE_NUMBER, body=msg)
        """
        severity = alert_data.get("severity", "INFO")
        title = alert_data.get("title", "Emergency Alert")
        affected_area = alert_data.get("affected_area", "General District")
        rec_action = alert_data.get("recommended_action", "Stay tuned to emergency broadcasts.")

        sms_body = f"[{severity} ALERT] {title} in {affected_area}. Action: {rec_action}"

        return {
            "provider": self.provider_name,
            "status": "SIMULATED_SUCCESS",
            "channel": "sms_gateway",
            "simulated_sms_body": sms_body,
            "note": "Production Twilio / AWS SNS integration stub ready for API keys.",
        }


class PushNotificationProvider(BaseNotificationProvider):
    """Mobile Push Notification Provider Stub (Firebase FCM / APNs integration point)."""

    @property
    def provider_name(self) -> str:
        return "PushNotification"

    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Push Notification dispatch for prototype without requiring paid API keys.

        Production Integration Notes:
        -----------------------------
        1. Install firebase-admin package: pip install firebase-admin
        2. Load service account JSON key credentials file
        3. Call messaging.send(messaging.Message(notification=..., topic='disaster_alerts'))
        """
        return {
            "provider": self.provider_name,
            "status": "SIMULATED_SUCCESS",
            "channel": "firebase_fcm_topic",
            "topic": f"hazard_alerts_{alert_data.get('severity', 'ALL').lower()}",
            "note": "Production Firebase FCM / APNs integration stub ready for credentials.",
        }


class EmailNotificationProvider(BaseNotificationProvider):
    """Email Notification Provider Stub (SendGrid / Amazon SES / SMTP integration point)."""

    @property
    def provider_name(self) -> str:
        return "Email"

    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Email dispatch for prototype without requiring paid API keys.

        Production Integration Notes:
        -----------------------------
        1. Install sendgrid or use python standard smtplib
        2. Set SENDGRID_API_KEY environment variable
        3. Format HTML disaster advisory template and send to subscriber list
        """
        return {
            "provider": self.provider_name,
            "status": "SIMULATED_SUCCESS",
            "channel": "smtp_sendgrid",
            "recipient_group": "district_disaster_officers@gov.in",
            "note": "Production SendGrid / Amazon SES integration stub ready.",
        }


class NotificationDispatcher:
    """Orchestrates notification dispatches across active and simulated providers based on severity."""

    def __init__(self):
        self.web_provider = DashboardWebNotificationProvider()
        self.sms_provider = SMSNotificationProvider()
        self.push_provider = PushNotificationProvider()
        self.email_provider = EmailNotificationProvider()

    def dispatch_alert_notifications(self, alert_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Dispatch alert to appropriate notification providers based on alert severity level."""
        severity = (alert_data.get("severity") or "INFO").upper()
        dispatches = []

        # 1. Web Dashboard Provider (Always Active)
        dispatches.append(self.web_provider.send_alert(alert_data))

        # 2. Email Provider (Active for WARNING, HIGH, CRITICAL)
        if severity in ["WARNING", "HIGH", "CRITICAL"]:
            dispatches.append(self.email_provider.send_alert(alert_data))

        # 3. Push Notification Provider (Active for HIGH, CRITICAL)
        if severity in ["HIGH", "CRITICAL"]:
            dispatches.append(self.push_provider.send_alert(alert_data))

        # 4. SMS Provider (Active for CRITICAL)
        if severity == "CRITICAL":
            dispatches.append(self.sms_provider.send_alert(alert_data))

        return dispatches


# Global singleton dispatcher instance
notification_dispatcher = NotificationDispatcher()
