# SIH26191 — Progressive Web App & Offline Emergency Architecture

> **Offline-First Capability & Caching Specification**

The SIH26191 Disaster Management Portal converts into a Progressive Web App (PWA) allowing field emergency personnel and citizens to access vital relief information during network outages.

---

## 🌟 Offline-First Architecture

```text
               User Device / Browser
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
   [ONLINE]                          [OFFLINE]
┌──────────────┐                 ┌──────────────┐
│  Live API    │                 │ Cache / SW   │
│  FastAPI DB  │                 │ IndexedDB    │
└──────────────┘                 └──────────────┘
       │                                 │
  Saves Shelters,                  Serves Stale
 Routes & Maps to                 Cached Data &
 Offline Storage                  Survival Guides
```

### 1. Service Worker Caching Strategy (`public/sw.js`)
- **Static App Shell & Leaflet Map Assets**: **Cache First** strategy (`/`, `/index.html`, `leaflet.css`, Leaflet marker icons, CartoDB basemap tiles).
- **Emergency API Data**: **Network First with Cache Fallback** strategy (`/api/v1/shelters`, `/api/v1/routes/calculate`, `/api/v1/hazards`). When network fetch fails, serves cached JSON from Service Worker cache or `offlineStorage`.

---

## 🛑 Data Staleness Warning & Honest UI Representation

- When internet connectivity is lost:
  - Top Banner displays: **`OFFLINE MODE — DISPLAYING CACHED EMERGENCY DATA`**.
  - Clearly states: *"Real-time live weather feeds unavailable. Displaying previously downloaded shelters and evacuation routes. Data may be stale."*
- **Policy**: The web application **NEVER falsely claims** that real-time live sensor updates or real-time radar data are active while offline.

---

## 📡 Peer-to-Peer Mesh Networking Specification (Bluetooth / Wi-Fi Direct)

### Limitation & Architecture Notice
- **Browser Security Sandbox Boundary**: Standard W3C web browser specifications (Chrome, Firefox, Safari) do **NOT** expose raw Bluetooth Mesh or Wi-Fi Direct peer-to-peer packet routing APIs due to security sandboxing.
- **Native Implementation Requirement**:
  - Peer-to-peer mesh packet forwarding requires a dedicated native mobile application (Android Java/Kotlin or iOS Swift) using:
    - **Android**: `NearbyConnectionsAPI` or `Wi-Fi Direct (P2P) Manager`.
    - **iOS**: `MultipeerConnectivity` framework.
- **Honest Representation**: SIH26191 does **NOT falsely represent** that standard web browser JavaScript can run native Bluetooth Mesh packet forwarding. Web PWA handles local client caching; native mobile SDKs handle mesh relaying.
