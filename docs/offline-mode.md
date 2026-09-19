# Feature 4 — Offline Deployment & Offline-First PWA

## Overview
The application is converted into an offline-capable Progressive Web App (PWA) that remains functional during internet outages, mobile tower destruction, power failures, or remote grid disconnection.

---

## Technical PWA Architecture

### Service Worker (`public/sw.js`)
- **Cache Strategy for Assets**: Cache-First for app shell (`index.html`, `manifest.json`, CSS, icons, Leaflet JS/CSS, map tiles).
- **Cache Strategy for APIs**: Network-First with Cache Fallback for `/api/v1/*`. If network fails, serves cached JSON payload with `X-Offline-Cached` header.

### Offline Local Storage (`services/offlineStorage.ts`)
- Persists cached relief shelters, evacuation routes, hazard map layers, animal safety records, emergency helpline contacts, and local queued changes to `localStorage` / `IndexedDB`.

---

## UI/UX Offline Indicators

```
+-----------------------------------------------------------------------+
|  OFFLINE MODE — Information may be outdated.                         |
|  Last Synchronization: 10:35 AM IST                                   |
|                                                                       |
|  Available offline:                                                  |
|  ✓ Emergency instructions                                             |
|  ✓ Saved evacuation routes                                             |
|  ✓ Shelter information                                                |
|  ✓ Emergency contacts                                                 |
|  ✓ Animal rescue information                                          |
|                                                                       |
|  IMPORTANT: Real-time hazard updates are unavailable.                 |
+-----------------------------------------------------------------------+
```

---

## Native Bluetooth Mesh & Wi-Fi Direct Architecture Specification

> [!NOTE]
> Web browser security sandboxes do not permit low-level raw Bluetooth Mesh or Wi-Fi Direct packet routing. Native Android (Wi-Fi P2P Manager / BLE Advertising) and iOS (Multipeer Connectivity) SDKs are required for raw mesh transport.

### Native Mobile Mesh Integration Blueprint
1. **Android Native Sidecar**: Implements `WifiP2pManager` and `BluetoothLeAdvertiser` to broadcast emergency JSON payloads between nearby devices without cellular networks.
2. **Web View Bridge**: Communicates via `window.NativeMeshBridge` to feed received offline peer messages into the PWA.

---

## Implementation Status
- [x] **IMPLEMENTED**: Service Worker (`public/sw.js`) & Web App Manifest (`public/manifest.json`)
- [x] **IMPLEMENTED**: Offline Storage Service & Sync Queue (`offlineStorage.ts`)
- [x] **IMPLEMENTED**: Network listener hooks (`online` / `offline` state detection)
- [x] **IMPLEMENTED**: Offline Emergency Page & status warning banners (`OfflineEmergencyPage.tsx`)
- [ ] **FUTURE INTEGRATION**: Native Android / iOS Bluetooth Mesh sidecar app wrapper
