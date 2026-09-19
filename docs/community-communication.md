# Feature 3 — Community Communication Web App

## Overview
The Community Communication Web App provides targeted, multi-channel disaster communications for emergency officials, rescue responders, local volunteers, and citizens.

---

## Message Categories
- `GENERAL`: General district updates
- `EVACUATION`: Official evacuation orders & routes
- `ANIMAL_SAFETY`: Animal rescue points & holding facility locations
- `SHELTER`: Shelter space availability & supply updates
- `ROAD_BLOCK`: Blocked highway detours & road conditions
- `WEATHER`: Rainfall forecast & hydrological updates
- `EMERGENCY`: Critical emergency broadcasts

---

## Notification Abstraction Layer Architecture

```
Community Communication Router (routers/communications.py)
                         │
                         ▼
             Notification Manager
                         │
        ┌────────────────┼────────────────┬────────────────┐
        ▼                ▼                ▼                ▼
   Mock SMS Provider  Mock Push Provider Mock Email Net  Gov Emergency Net
```

The system includes an abstraction layer (`abstract_notifier.py`) allowing future drop-in integrations with commercial SMS gateways (Twilio / ISO SMS), Push notification servers (FCM / WebPush), and Government emergency warning systems.

---

## REST APIs
- `POST /api/v1/communications/messages`: Create community announcement.
- `GET /api/v1/communications/messages`: List messages (filtered by category or target area).
- `POST /api/v1/communications/emergency-broadcast`: Dispatch emergency broadcast to target sector.

---

## Implementation Status
- [x] **IMPLEMENTED**: Community communication database models & schemas
- [x] **IMPLEMENTED**: Multi-channel notification abstraction layer
- [x] **IMPLEMENTED**: Category & geographic area filter queries
- [x] **IMPLEMENTED**: Frontend Community Communication Center (`CommunityCommunicationPage.tsx`)
- [ ] **FUTURE INTEGRATION**: Real SMS Gateway provider credentials (Twilio / Gov SMS)
