# Dynamic Hospital Management and Emergency Response Plan

## 1. Existing Architecture Overview

The SIH26191 Disaster Management Platform currently consists of:
- **Backend**: FastAPI Application with SQLAlchemy database models (PostgreSQL / SQLite), providing endpoints for Weather, Hazard Zones, Shelters, Relocation, Animals, Alerts, and Communication.
- **Frontend**: React + TypeScript + Vite web app styled with Vanilla CSS / Tailwind utilities, using Leaflet/Google Map components (`DisasterMap.tsx`) with layer toggle support (`MapLayers.tsx`), PWA offline support, AI Assistant (`AIAssistantPage.tsx`), and PDF generation via `reports.py`.
- **Primary Single Map (`DisasterMap.tsx`)**: Displays weather overlays (rainfall, temperature, wind), hazard red zones, safe zones, human shelters, animal shelters, evacuation routes, and relocation areas on a unified Leaflet/Google tile container.

---

## 2. Dynamic Hospital Management Feature Architecture

The new **Dynamic Hospital Management and Emergency Response** subsystem adds comprehensive healthcare infrastructure tracking to the existing disaster response stack:

```
                          +-----------------------------------+
                          |          ONE GOOGLE MAP           |
                          |  (Tile Layer + Feature Overlay)   |
                          +-----------------+-----------------+
                                            |
        +------------------+----------------+-------------------+-------------------+
        |                  |                |                   |                   |
  Weather Layer     Hazard Red Zone     Shelters Layer    Evacuation Layer    HOSPITALS LAYER
  (Rain/Temp/Wind)   (Polygon/Risk)    (Human & Animal)   (Safe Path Line)    (Hospital Markers)
                                                                                    |
                                                                                    v
                                                                          +--------------------+
                                                                          |  Hospital Marker   |
                                                                          | & Details Sidepanel|
                                                                          +--------------------+
```

### Key Architectural Components:
1. **Hospital Provider Abstraction Layer (`HospitalDataProvider`)**:
   - `DatabaseHospitalProvider`: Queries locally managed hospital records & capacity logs updated by system admins.
   - `ExternalHospitalAPIProvider`: Extensible interface for integrating real-time state health department / hospital management system APIs.
2. **Dynamic Capacity Calculation & Audit Engine**:
   - `Available Beds = Total Beds - Occupied Beds`
   - `Available ICU = Total ICU - Occupied ICU`
   - `Available Emergency Beds = Total Emergency Beds - Occupied Emergency Beds`
   - Validates `occupied <= total` and `available >= 0`.
   - Records immutable audit history in `hospital_updates` on every capacity modification.
3. **Multi-Factor Hospital Recommendation Engine (`POST /api/v1/hospitals/recommend`)**:
   - Ranks hospitals serving a Red Zone based on:
     1. Emergency capability & Operational Status (`OPEN` > `EMERGENCY_ONLY` > `LIMITED`)
     2. Available Emergency Beds & ICU Capacity
     3. Distance & Travel Time from Red Zone centroid
     4. Required Specialization & Ambulance availability
4. **Disaster Flow Integration**:
   - `Rainfall/Disaster Event -> Risk Analysis -> Red Zone -> Affected Population -> Medical Need -> Hospital Capacity Search -> Hospital Recommendation -> Safe Route Navigation -> Emergency Alert Broadcast -> PDF Analysis`.

---

## 3. Database Schema Changes

New database tables added to `backend/app/models/entities.py` (with SQLAlchemy & Pydantic models):

### 1. `hospitals`
- `id` (Integer, Primary Key)
- `hospital_id` (String(100), Unique, Index)
- `name` (String(255), Index, Nullable=False)
- `type` (String(100), Nullable=False) -- Government, Private, Public Medical College, District Hospital, CHC, PHC, Specialty, Trauma Centre
- `address` (String(500))
- `latitude` (Float, Nullable=False)
- `longitude` (Float, Nullable=False)
- `district` (String(255), Index)
- `state` (String(255), Index)
- `phone` (String(50))
- `emergency_status` (String(50), Default="OPEN") -- OPEN, LIMITED, FULL, EMERGENCY_ONLY, CLOSED, UNKNOWN
- `operational_status` (String(50), Default="OPEN")
- `specialization` (String(255))
- `data_source` (String(100), Default="Hospital Management System") -- Google Maps / Places, Hospital Management System, Hospital API
- `created_at`, `updated_at`

### 2. `hospital_capacity`
- `id` (Integer, Primary Key)
- `hospital_id` (Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), Unique)
- `total_beds` (Integer, Default=0)
- `occupied_beds` (Integer, Default=0)
- `available_beds` (Integer, Default=0)
- `total_icu` (Integer, Default=0)
- `occupied_icu` (Integer, Default=0)
- `available_icu` (Integer, Default=0)
- `total_emergency_beds` (Integer, Default=0)
- `occupied_emergency_beds` (Integer, Default=0)
- `available_emergency_beds` (Integer, Default=0)
- `total_ambulances` (Integer, Default=0)
- `available_ambulances` (Integer, Default=0)
- `updated_at` (DateTime)

### 3. `hospital_updates` (Audit Log)
- `id` (Integer, Primary Key)
- `hospital_id` (Integer, ForeignKey("hospitals.id"))
- `field_name` (String(100))
- `old_value` (String(255))
- `new_value` (String(255))
- `updated_by` (String(255))
- `timestamp` (DateTime, Default=now)

---

## 4. Backend API Endpoints (`/api/v1/hospitals`)

- `GET /api/v1/hospitals`: List all hospitals with layer filter support.
- `GET /api/v1/hospitals/{id}`: Get hospital details & capacity.
- `POST /api/v1/hospitals`: Add a new hospital (Admin Only).
- `PATCH /api/v1/hospitals/{id}`: Update hospital info/status (Admin Only).
- `GET /api/v1/hospitals/{id}/capacity`: Get capacity data & last updated timestamp.
- `PATCH /api/v1/hospitals/{id}/capacity`: Update capacity metrics (Admin Only, writes audit log).
- `GET /api/v1/hospitals/nearby`: Find hospitals within radius of lat/lon or location name.
- `GET /api/v1/hospitals/available`: Filter hospitals with available emergency/ICU beds.
- `POST /api/v1/hospitals/recommend`: Multi-factor recommendation algorithm for Red Zone medical emergencies.
- `POST /api/v1/hospitals/{id}/updates`: Fetch historical audit log for a hospital.

---

## 5. Frontend UI & Single Map Integration

1. **Single Google Map Layer (`DisasterMap.tsx` & `MapLayers.tsx`)**:
   - Add `hospitals: boolean` toggle inside `RESPONSE` category of `MapLayers.tsx`.
   - Render hospital markers (🏥 icon with color coding: 🟢 Open, 🟡 Limited, 🔴 Full, 🟠 Emergency Only, ⚫ Closed, ⚪ Unknown).
   - Marker Popup & Slide-over Details Panel showing real capacity, distance, estimated travel time, and `[Start Medical Emergency Route]` action.
2. **Admin Hospital Management Page (`HospitalsPage.tsx`)**:
   - Admin view with hospital data table, search/filter, capacity edit modal, status toggle, and audit history.
3. **Medical Emergency Action in Red Zone Analysis**:
   - "🚨 MEDICAL EMERGENCY" button in `RedZoneAnalysis.tsx` triggering immediate hospital recommendation & route drawing on the single map.
4. **Overview Dashboard & System Health Integration**:
   - Hospital capacity summary metrics & utilization progress bars (`Bed Utilization %`, `ICU Utilization %`, `Emergency Utilization %`).

---

## 6. Role Permissions Matrix

| Action / Capability | CITIZEN / PUBLIC (USER) | COMMAND OFFICER (ADMIN) |
|---|:---:|:---:|
| View Hospitals & Map Layer | ✅ | ✅ |
| Search Hospitals by Location | ✅ | ✅ |
| View Capacity & Emergency Status | ✅ | ✅ |
| Request Medical Recommendation | ✅ | ✅ |
| View Evacuation Route to Hospital | ✅ | ✅ |
| Add / Edit Hospital Info | ❌ | ✅ |
| Update Capacity / ICU / Ambulances | ❌ | ✅ |
| Change Operational Status | ❌ | ✅ |
| Deactivate / Merge Hospitals | ❌ | ✅ |
| Generate Official PDF Report with Hospital Analysis | ❌ | ✅ |

---

## 7. Disaster Flow & Route Integration

1. **Red Zone Detection**: High rainfall / flood risk identifies affected area.
2. **Medical Needs Evaluation**: Calculates patient casualties / emergency medical demand based on affected population.
3. **Hospital Recommendation Engine**: Filters nearby operational hospitals with adequate available emergency beds & ICU.
4. **Safe Routing**: Calculates shortest safe path from Red Zone to recommended hospital avoiding hazard polygons.

---

## 8. PDF Report Integration

Updates `backend/app/routers/reports.py` so the existing Admin PDF generator includes:
- Total Hospitals, Operational Status breakdown (Open/Limited/Full/Emergency Only).
- Total / Occupied / Available Beds, ICU Beds, Emergency Beds, Ambulances.
- Bed & ICU Utilization Percentages.
- Recommended Hospitals assigned to active Red Zones.
- Embedded map snapshot with hospital markers.

---

## 9. Deduplication & Offline Caching Strategy

1. **Deduplication Script (`scripts/deduplicate_hospitals.py`)**:
   - Detects duplicate records sharing identical hospital name & coordinates (or duplicate Google Place ID).
   - Merges records, preserves capacity audit logs, and logs merged changes.
2. **Offline Support (`OfflineEmergencyPage.tsx` & Service Worker)**:
   - Caches hospital locations, contact phone numbers, emergency instructions, and last known capacity data into IndexedDB / LocalStorage.
   - Displays clear badge: `OFFLINE MODE - Last synchronized: <timestamp>`.
