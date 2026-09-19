# Comprehensive System Audit: SIH26191 Disaster Management Platform

**Audit Date**: September 4, 2026  
**Audited Target**: Full Workspace (`backend/`, `frontend/`, `database/`, `gis/`, `ml/`, `relocation/`, `tests/`)

---

## 1. Existing Frontend Pages
The application currently contains 16 frontend page views in `frontend/src/pages/`:
1. `OverviewDashboard.tsx` — Main command center dashboard metrics.
2. `UserDashboard.tsx` — Citizen safety portal dashboard.
3. `LiveHazardMap.tsx` — Primary Leaflet map rendering hazard zones and shelters.
4. `RedZoneAnalysis.tsx` — Detailed hazard score and Red Zone breakdown page.
5. `SheltersPage.tsx` — Relief shelter list and resource tracking.
6. `CarryingCapacityPage.tsx` — Duplicate carrying capacity metric page.
7. `EvacuationPlanningPage.tsx` — Dijkstra evacuation routing page (instantiates duplicate MapContainer).
8. `RelocationPlanPage.tsx` — Relocation optimization solver view.
9. `AnimalSafetyPage.tsx` — Animal safety and rescue management.
10. `CommunityCommunicationPage.tsx` — Emergency announcements and broadcasts.
11. `AIAssistantPage.tsx` — Grounded AI decision-support assistant.
12. `DisasterSimulationPage.tsx` — 16-step disaster simulation runner.
13. `AlertsPage.tsx` — Disaster alert list and manual SOS controls.
14. `OfflineEmergencyPage.tsx` — Offline PWA emergency guide.
15. `SystemHealthPage.tsx` — Database and system diagnostics page.
16. `LoginPage.tsx` — User authentication and role selection.

---

## 2. Existing Backend APIs
The FastAPI backend (`backend/app/routers/`) currently exposes:
- `/health` — Health check endpoint.
- `/api/v1/auth/*` — User authentication (`login`, `me`).
- `/api/v1/shelters/*` — Shelter CRUD and capacity endpoints.
- `/api/v1/hazard-zones` & `/api/v1/hazards` — Hazard zone endpoints.
- `/api/v1/population` — Population distribution endpoints.
- `/api/v1/rainfall/*` — Rainfall records and live weather mock endpoints.
- `/api/v1/risk/predict` — ML XGBoost risk classifier.
- `/api/v1/routes/calculate` — Dijkstra safe evacuation route solver.
- `/api/v1/relocation/plan` — Relocation optimizer solver.
- `/api/v1/simulation/run` — 16-step disaster simulation pipeline.
- `/api/v1/alerts/*` — Emergency alert endpoints and manual SOS triggers.
- `/api/v1/assistant/chat` — Grounded AI Assistant chat endpoint.
- `/api/v1/animals/*` — Animal safety and animal shelters endpoints.
- `/api/v1/communications/*` — Community messages and emergency broadcasts.
- `/download-pdf` — Root static PDF download endpoint.

---

## 3. Existing Database Tables
The SQLAlchemy database schema (`backend/app/models/entities.py`) includes 15 entities:
1. `users` — User credentials and roles (`admin`, `responder`, `user`).
2. `locations` — District/State locations with SpatialPoint coordinates.
3. `population` — Sector population and vulnerability records with SpatialPolygon.
4. `shelters` — Relief shelters with capacity limit constraints.
5. `shelter_resources` — Water, food, medical, and sanitation inventory.
6. `roads` — Passable/flooded road network with SpatialLineString.
7. `hazard_zones` — Risk level polygons (`CRITICAL`, `HIGH`, `MODERATE`, `LOW`).
8. `rainfall_records` — Station rainfall measurements.
9. `disaster_events` — Historical disaster event logs.
10. `evacuation_routes` — Safe Dijkstra route paths.
11. `relocation_assignments` — Evacuee to shelter allocations.
12. `alerts` — System emergency notifications.
13. `animals` — Registered livestock and pets.
14. `animal_shelters` — Dedicated animal holding facilities.
15. `communication_messages` — Official announcements and broadcasts.
16. `alert_audit_logs` — Audit log of alert actions and SOS triggers.

---

## 4. Existing Map Components
- `LiveHazardMap.tsx`: Main map rendering Leaflet `MapContainer`, tiles, polygons, markers, and popups.
- `EvacuationPlanningPage.tsx`: Instantiates a second `MapContainer` with redundant Leaflet tile initialization and marker setup.

---

## 5. Existing Weather Components
- Static/mock rainfall data in `backend/app/services/rainfall_service.py`.
- No live Open-Meteo or OpenWeatherMap API integration yet.
- No India-wide coordinate geocoding or location search box yet.

---

## 6. Existing Report/PDF Functionality
- `backend/app/main.py` contains a static file endpoint `/download-pdf` serving a pre-compiled static PDF file (`Disaster_Platform_Detailed_Overview_and_Workflows.pdf`).
- There is no dynamic PDF report generation service or Admin-only report filter UI.

---

## 7. Duplicate Functionality Found
1. **Map Rendering**: Duplicated in `LiveHazardMap.tsx` and `EvacuationPlanningPage.tsx`.
2. **Shelter & Capacity**: Split between `SheltersPage.tsx` and `CarryingCapacityPage.tsx`.
3. **Data Fetching**: Component-level redundant `fetch` calls across pages instead of centralized service layers.
4. **Backend Router Paths**: `hazard_zones.py` registers both `/api/v1/hazard-zones` and `/api/v1/hazard_zones`.

---

## 8. Components to be Removed / Refactored
- Remove duplicate `MapContainer` instances inside individual feature pages.
- Remove hardcoded mock weather responses in `rainfall_service.py`.
- Remove static PDF link in header and replace with dynamic Admin-only PDF generation.

---

## 9. Components to be Merged
- Merge `LiveHazardMap.tsx` and `EvacuationPlanningPage.tsx` map logic into **One Central Reusable Component**: `frontend/src/components/map/DisasterMap.tsx`.
- Merge `CarryingCapacityPage.tsx` functionality directly into `SheltersPage.tsx`.
- Centralize frontend data services into:
  - `frontend/src/services/weatherService.ts`
  - `frontend/src/services/hazardService.ts`
  - `frontend/src/services/shelterService.ts`
  - `frontend/src/services/reportService.ts`

---

## 10. Recommended Final Architecture

```
                                SINGLE PRIMARY MAP EXPERIENCE
                               (DisasterMap.tsx + Layers Control)
                                               │
       ┌──────────────────┬────────────────────┼───────────────────┬──────────────────┐
       ▼                  ▼                    ▼                   ▼                  ▼
  Live Weather       Hazard Zones       Relief Shelters     Evacuation Routes   Animal Safety
 (Open-Meteo API)  (ML XGBoost Model)  (Human & Animal)   (Dijkstra Detour)  (Rescue Facilities)
       │                  │                    │                   │                  │
       └──────────────────┴────────────────────┼───────────────────┴──────────────────┘
                                               ▼
                                      DISASTER RISK ENGINE
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       ▼                       ▼                       ▼
               AI ASSISTANT CHAT         EMERGENCY SOS          ADMIN PDF REPORT
             (Grounded DB Context)     (Audio Synthesizer)    (ReportLab Backend)
```
