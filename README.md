# SIH26191 — Intelligent Hazard Red Zone Mapping, Carrying Capacity Assessment & Relocation System

> **Smart India Hackathon Problem Statement 26191**  
> Spatial-AI disaster management platform delivering machine-learning hazard risk mapping, multi-factor shelter carrying capacity scoring, NetworkX Dijkstra safe evacuation routing, deterministic relocation optimization, and an offline-first PWA control center.

---

## 🏗️ Architecture & Technology Stack

```text
[ React 18 + TS + Tailwind + Leaflet PWA ]
                      │
                      ▼ (Nginx Reverse Proxy :80)
┌───────────────────────────────────────────────────────────┐
│                    FastAPI Backend Engine                 │
│  ├── GIS Baseline Engine (Rasterio/Shapely/PyProj)        │
│  ├── ML Hazard Predictor (XGBoost Classifier)              │
│  ├── Dynamic Routing Engine (NetworkX Dijkstra)           │
│  ├── Relocation Optimizer (Multi-Objective Solver)        │
│  ├── Alert System (Multi-Channel Dispatcher)             │
│  └── Disaster Simulation Engine (9-Step Workflow)         │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
                 [ PostGIS PostgreSQL DB :5432 ]
```

---

## 🚀 Quick Start & Development Setup

### 1. Prerequisites
- Python 3.10+ & Virtual Environment (`.venv`)
- Node.js 18+ & npm
- PostgreSQL 15 + PostGIS 3.3 (or Docker Desktop)

### 2. Local Backend Setup
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI Uvicorn Server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 3. Local Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite Development Server
npm run dev
```
- Access Frontend Control Center: `http://localhost:5173`

---

## 🐳 Production Docker Deployment

### 1. Environment Configuration
Copy `.env.example` to `.env` and set your secure passwords & secret keys:
```bash
cp .env.example .env
```

### 2. Launch Production Stack via Docker Compose
```bash
# Build and launch all containerized services (DB, FastAPI, NGINX, PWA Frontend)
docker compose -f docker-compose.prod.yml up -d --build
```

### 3. Verify Container Health
```bash
# Inspect container status and healthchecks
docker compose -f docker-compose.prod.yml ps

# Tail application logs
docker compose -f docker-compose.prod.yml logs -f backend
```

### 4. Database Migration & Initialization
The PostGIS container automatically runs `database/init.sql` on initial startup. To force re-initialization or run database migrations manually:
```bash
docker exec -i sih_postgis_db_prod psql -U sih_user -d sih_disaster_db < database/init.sql
```

---

## 🧪 Running Automated Tests & Verification

### Run Backend PyTest Suite (61 Automated Tests)
```bash
.\.venv\Scripts\pytest -v tests/
```

### Run 12-Step End-to-End Scenario Verification
```bash
.\.venv\Scripts\python scripts/verify_e2e_scenario.py
```

### Build Production React PWA Bundle
```bash
cd frontend && npm run build
```

---

## 📡 Deployment Status & Cloud Disclaimer

> **Honest Representation Statement**:
> The SIH26191 application has been containerized into production-ready Docker containers (`docker-compose.prod.yml`) verified locally on developer infrastructure. Cloud hosting (e.g. AWS ECS / Kubernetes / DigitalOcean) deployment manifests are provided; live cloud deployment can be launched using the provided Docker Compose file on any cloud VM or container instance.

---

---

## 🌟 Integrated Major Features

1. **Feature 1: AI Disaster Management Assistant** — Grounded decision-support tool (`POST /api/v1/assistant/chat`) answering queries on Red Zones, affected population, shelter capacity, and evacuation routes without hallucinating statistics.
2. **Feature 2: Emergency SOS Sound Alert** — Visual and audible SOS alarm system (Web Audio API synthesizer `... --- ...`) with browser permission unlock, mute toggles, manual admin triggers, and audit logging.
3. **Feature 3: Animal Safety & Community Communication** — Dedicated animal registration, animal shelters with capacity separation from human shelters, animal rescue optimizer, community messaging feed, and multi-channel emergency broadcast dispatcher.
4. **Feature 4: Offline-First PWA & Deployment** — Offline PWA (`sw.js` service worker, IndexedDB / local storage caching) displaying network status, cached resources, and sync queue.

---

## 📜 Documentation Index

- [`docs/ai-assistant.md`](file:///c:/SIH%20FINAL%20PROJECT/docs/ai-assistant.md) — AI Disaster Assistant Architecture & APIs
- [`docs/sos-alerts.md`](file:///c:/SIH%20FINAL%20PROJECT/docs/sos-alerts.md) — Emergency SOS Sound Alert System Specification
- [`docs/animal-safety.md`](file:///c:/SIH%20FINAL%20PROJECT/docs/animal-safety.md) — Animal Safety & Capacity Separation Architecture
- [`docs/community-communication.md`](file:///c:/SIH%20FINAL%20PROJECT/docs/community-communication.md) — Community Communication & Broadcast Center
- [`docs/offline-mode.md`](file:///c:/SIH%20FINAL%20PROJECT/docs/offline-mode.md) — Offline PWA & Native Mesh Architecture
- [`docs/test_report.md`](file:///c:/SIH%20FINAL%20PROJECT/docs/test_report.md) — Automated Test Suite Report (70 Tests Passing)
- [`docs/security_audit.md`](file:///c:/SIH%20FINAL%20PROJECT/docs/security_audit.md) — Security Audit & Production Readiness

