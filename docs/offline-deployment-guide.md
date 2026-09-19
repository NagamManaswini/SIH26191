# Standalone Offline & PWD Field Deployment Guide

## 1. Executive Summary
During severe disaster events (e.g. landslides, cyclones, cloudbursts, severe floods), power grids, internet exchanges, and cellular telecom towers are often destroyed or severed. 

This platform supports **100% Disconnected Offline Deployment** allowing Public Works Department (PWD) field engineers, National Disaster Response Force (NDRF), District Emergency Operating Centers (DEOC), and relief camp officers to operate on standalone laptops or local Wi-Fi / LAN routers without any cloud or internet connectivity.

---

## 2. Key Offline Capabilities

| Capability | Online Mode | Offline Field / PWD Mode |
| :--- | :--- | :--- |
| **Database** | PostgreSQL + PostGIS | Standalone Embedded SQLite (`sih_disaster.db`) |
| **Frontend Serving** | Vite Dev / Cloud CDN | Production PWA bundle cached via Service Worker (`sw.js`) |
| **Hazard & Shelter Data** | Real-time live feeds & PostGIS | Pre-seeded SQLite tables + localStorage cache bundle |
| **Evacuation Routing** | NetworkX Dijkstra on server | Cached safe detours + Dijkstra local computation |
| **Data Exchange** | Cloud REST API & WebSockets | JSON Offline Bundle Export / Import (USB sticks / Mesh) |
| **PWA App Installation** | Chrome/Edge/Safari Install | Desktop & Mobile Standalone App (Service Worker Cache) |

---

## 3. Quick Start — 1-Click Field Launch

### Option A: Windows (Field Laptops / PWD Workstations)
Double-click:
```cmd
deploy_offline.bat
```
Or run in PowerShell / Command Prompt:
```cmd
python run_offline.py
```

### Option B: Linux / Raspberry Pi / Edge Node
```bash
chmod +x deploy_offline.sh
./deploy_offline.sh
```

---

## 4. Progressive Web App (PWA) Offline Usage

1. **Pre-caching on First Access**:
   - When opened in Google Chrome, Microsoft Edge, Safari, or Firefox, the Service Worker (`public/sw.js`) automatically pre-caches the HTML shell, icons, stylesheets, map tiles, and emergency relief datasets.
2. **App Installation**:
   - Click the **"INSTALL PWA"** button in the top navigation bar or browser address bar to install the application as a standalone desktop/mobile app.
3. **Disconnected Execution**:
   - Disconnect Wi-Fi/Ethernet or enable Airplane Mode.
   - The platform will display the **"OFFLINE PWA ACTIVE"** badge.
   - All shelters, emergency hotline contacts, hospitals, livestock safety centers, and evacuation detour routes remain accessible.

---

## 5. Field Data Synchronization via USB (For Air-Gapped Zones)

1. **Exporting from Command Center**:
   - Navigate to **Offline Mode** in the sidebar.
   - Click **"Export Offline Bundle"** to save `Disaster_Offline_Emergency_Bundle.json` to a USB flash drive.
2. **Importing at Field Station / Camp**:
   - Insert USB drive into field laptop.
   - Open portal -> **Offline Mode** -> Click **"Import Bundle"**.
   - Select the JSON file to instantly sync shelters, hospital capacities, and safe detour routes without internet.

---

## 6. PWD Road Clearance & Route Optimization

Field PWD officers can use the system offline to:
- View blocked landslide/flood road segments in Red Zones.
- Assess safe bypass routes and detour distances.
- Coordinate livestock evacuation safe holding capacities.
