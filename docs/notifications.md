# SIH26191 — Notification Provider Integration Architecture

> **Multi-Channel Alert Notification Abstraction Layer**

The SIH26191 platform provides an abstract provider system for dispatching multi-channel emergency notifications (Web Dashboard, SMS, Push, and Email).

---

## 🏗️ Architecture & Dispatch Flow

All alert dispatches inherit from `BaseNotificationProvider` ([`backend/app/services/notifications/base.py`](file:///c:/SIH%20FINAL%20PROJECT/backend/app/services/notifications/base.py)) and are orchestrated by `NotificationDispatcher`.

```text
POST /api/v1/alerts
       │
       ▼
Alert DB Record Created
       │
       ▼
NotificationDispatcher
 ├── DashboardWebNotificationProvider [Active - Local Event Stream]
 ├── EmailNotificationProvider        [Active for WARNING, HIGH, CRITICAL]
 ├── PushNotificationProvider         [Active for HIGH, CRITICAL]
 └── SMSNotificationProvider          [Active for CRITICAL]
```

---

## 🔌 Provider Integration Details

### 1. Dashboard Web Notification Provider (`DashboardWebNotificationProvider`)
- **Status**: **ACTIVE** (Default for prototype demo).
- **Channel**: Real-time Web Dashboard WebSocket & event stream.
- **Cost**: $0 / Free.

---

### 2. SMS Provider (`SMSNotificationProvider`)
- **Target External API**: Twilio / AWS SNS / Gupshup SMS Gateway.
- **Production Integration Steps**:
  1. Install SDK: `pip install twilio`
  2. Set environment variables in `.env`:
     ```env
     TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx
     TWILIO_AUTH_TOKEN=your_auth_token
     TWILIO_PHONE_NUMBER=+18005550199
     ```
  3. Replace stub body in [`backend/app/services/notifications/providers.py`](file:///c:/SIH%20FINAL%20PROJECT/backend/app/services/notifications/providers.py#L42):
     ```python
     from twilio.rest import Client

     client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
     message = client.messages.create(
         body=sms_body,
         from_=os.environ["TWILIO_PHONE_NUMBER"],
         to=recipient_phone
     )
     ```

---

### 3. Push Notification Provider (`PushNotificationProvider`)
- **Target External API**: Firebase Cloud Messaging (FCM) / Apple Push Notification service (APNs).
- **Production Integration Steps**:
  1. Install SDK: `pip install firebase-admin`
  2. Initialize FCM with service account credentials:
     ```python
     import firebase_admin
     from firebase_admin import credentials, messaging

     cred = credentials.Certificate("path/to/serviceAccountKey.json")
     firebase_admin.initialize_app(cred)

     message = messaging.Message(
         notification=messaging.Notification(
             title=alert_data["title"],
             body=alert_data["message"],
         ),
         topic="disaster_critical_alerts",
     )
     response = messaging.send(message)
     ```

---

### 4. Email Notification Provider (`EmailNotificationProvider`)
- **Target External API**: SendGrid / Amazon SES / Standard SMTP.
- **Production Integration Steps**:
  1. Install SDK: `pip install sendgrid`
  2. Set environment variable: `SENDGRID_API_KEY=SG.xxxx`
  3. Call SendGrid Mail API to transmit HTML emergency advisory templates.
