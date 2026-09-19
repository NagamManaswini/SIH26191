# Feature 2 — Emergency SOS Sound Alert System

## Overview
The Emergency SOS Alert system visually and audibly notifies users when critical disaster conditions occur (Factor of Safety < 1.0, CRITICAL hazard level, manual administrator trigger, or emergency evacuation execution).

---

## Severity Matrix & Triggers

| Severity | Color Code | Audio Behavior | Trigger Condition |
| :--- | :--- | :--- | :--- |
| **INFO** | Blue | Silent | Weather update / General advisory |
| **WARNING** | Yellow | Subtle tone | Moderate rainfall / Waterlogging |
| **HIGH** | Orange | Single Warning Beep | High slope movement / Heavy rainfall |
| **CRITICAL** | Red | **Repeating SOS Tone (... --- ...)** | Landslide threat, FoS < 1.0, Manual Admin Trigger |

---

## Audio Permission & Browser Autoplay Rules
Browsers enforce strict autoplay policies blocking automatic audio playback.
The system implements:
1. **Audio Unlock Button**: "Enable Emergency Audio" initializes Web Audio API `AudioContext` on user interaction.
2. **Web Audio Synthesizer**: Uses native oscillators emitting `880Hz` international SOS tone pattern (`... --- ...`) eliminating missing asset issues.
3. **Mute/Unmute Toggle**: Allows operators to mute repeating audio alarm while retaining visual alerts.
4. **Visual Fallback**: High-visibility flashing emergency modal overlay (`EmergencySOSModal.tsx`).

---

## Database Schemas & Audit Logging

### `Alert` Model Fields
- `id`: Integer Primary Key
- `title`: String
- `message`: Text
- `severity`: Enum (`INFO`, `WARNING`, `HIGH`, `CRITICAL`)
- `affected_area`: String
- `recommended_action`: Text
- `status`: Enum (`ACTIVE`, `ACKNOWLEDGED`, `RESOLVED`, `EXPIRED`)

### `AlertAuditLog` Model Fields
- `id`: Integer Primary Key
- `alert_id`: Foreign Key (`alerts.id`)
- `action`: `MANUAL_SOS_TRIGGERED`, `SOS_STOPPED`, `ACKNOWLEDGED`, `MUTED`
- `performed_by`: Officer identity
- `timestamp`: DateTime

---

## REST APIs
- `POST /api/v1/alerts/sos-trigger`: Trigger manual CRITICAL emergency SOS alert.
- `POST /api/v1/alerts/sos-stop/{id}`: Deactivate active emergency SOS alarm.
- `POST /api/v1/alerts/{id}/acknowledge`: Record official acknowledgement.
- `GET /api/v1/alerts/audit-logs`: Fetch audit history.

---

## Implementation Status
- [x] **IMPLEMENTED**: Web Audio API SOS synthesizer service (`sosSoundService.ts`)
- [x] **IMPLEMENTED**: Visual emergency alert modal overlay (`EmergencySOSModal.tsx`)
- [x] **IMPLEMENTED**: Audio permission unlock, test tone, and mute toggles
- [x] **IMPLEMENTED**: Backend manual SOS trigger, deactivation, and audit log persistence
- [ ] **FUTURE INTEGRATION**: Integration with physical emergency siren hardware relays
