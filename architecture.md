# System Architecture Document: SIH26191 — Intelligent Disaster Management Platform

## 1. System Overview
**SIH26191 — Intelligent Hazard-Based Red Zone Mapping, Carrying Capacity Assessment & Relocation System** is an end-to-end, spatial-AI disaster response and preparedness platform. The application combines GIS spatial analysis, Machine Learning risk prediction, shelter capacity tracking, real-time safe evacuation routing, and optimal relocation planning.

---

## 2. Technical Stack Matrix
| Domain | Technologies |
| :--- | :--- |
| **Frontend** | React 18 (TypeScript), Vite, TailwindCSS / Custom CSS, Leaflet / MapLibre GL, Lucide Icons, PWA / Service Worker (Offline Cache) |
| **Backend API** | Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic, Uvicorn |
| **Database & Spatial** | PostgreSQL 16 + PostGIS 3.4, GeoAlchemy2 |
| **GIS Processing** | GeoPandas, Shapely, PyProj, Rasterio, GDAL |
| **Machine Learning** | XGBoost, scikit-learn, Joblib, NumPy, Pandas |
| **Routing Engine** | NetworkX, SciPy, Custom Dijkstra / A* with hazard dynamic edge weights |
| **Containerization** | Docker, Docker Compose, Multi-stage builds |
| **Testing** | PyTest (Backend/GIS/ML), Vitest / React Testing Library (Frontend) |

---

## 3. High-Level Architecture Diagram
```mermaid
flowchart TB
    subgraph Client Layer
        Admin[Admin Dashboard - React + TS]
        Public[Public Evacuation Dashboard - PWA/Offline Cache]
    end

    subgraph API Gateway / Backend Layer [FastAPI Application]
        AuthModule[Auth & User Management]
        HazardAPI[Hazard & Red Zone Endpoints]
        ShelterAPI[Shelter & Capacity Endpoints]
        EvacAPI[Routing & Evacuation Endpoints]
        RelocAPI[Relocation Optimization Endpoints]
    end

    subgraph Spatial & Intelligence Engine
        GISEngine[GIS Engine - GeoPandas/Rasterio/Shapely]
        MLEngine[ML Engine - XGBoost Hazard Prediction]
        RoutingEngine[Routing Engine - NetworkX / Red-Zone-Weighted Dijkstra]
        OptEngine[Relocation Optimization - Dynamic Capacity Allocation]
    end

    subgraph Data & Storage Layer
        PostGIS[(PostgreSQL + PostGIS)]
        RasterStore[(Raster & GeoTIFF Store)]
        ModelRegistry[(Trained ML Models / Artifacts)]
    end

    Client Layer -->|REST API / GeoJSON| API Gateway / Backend Layer
    API Gateway / Backend Layer --> GISEngine
    API Gateway / Backend Layer --> MLEngine
    API Gateway / Backend Layer --> RoutingEngine
    API Gateway / Backend Layer --> OptEngine
    API Gateway / Backend Layer --> PostGIS
    GISEngine --> RasterStore
    MLEngine --> ModelRegistry
```

---

## 4. Module Specifications

### 4.1 Frontend (`frontend/`)
- **Admin Dashboard**: Manages hazard layers, triggers ML risk assessment models, monitors shelter capacities, oversees evacuation routes, and reviews relocation allocation plans.
- **Public Evacuation Dashboard**: Mobile-first, lightweight interface allowing citizens to query safe evacuation routes from their current GPS location to the nearest safe shelter, view active Red Zones, and access offline emergency information.
- **GIS Map Viewer**: Interactive Leaflet/MapLibre map rendering vector Red Zones, hazard intensity rasters, shelter icons with live capacity indicators, and safe evacuation paths.

### 4.2 Backend (`backend/`)
- **FastAPI Core**: Modular architecture with versioned API routes (`/api/v1/...`).
- **Data Models**: Pydantic schemas for data validation and SQLAlchemy spatial entities mapped to PostGIS tables.
- **Async Task Execution**: Background execution for heavy GIS layer processing and ML batch inference.

### 4.3 GIS Engine (`gis/`)
- **Raster Processing**: Computes slope, aspect, elevation, flow accumulation, and rainfall intensity metrics using Rasterio.
- **Red Zone Delineation**: Converts continuous ML hazard probability rasters into multi-tiered polygon zones (Red: Extreme Risk, Yellow: Moderate Risk, Green: Safe).
- **Buffer & Spatial Query**: Spatial intersections of roads and buildings with buffer zones surrounding active hazard sites.

### 4.4 ML Risk Engine (`ml/`)
- **Risk Assessment**: XGBoost gradient boosted classifier/regressor trained on topographical (slope, elevation), geological, soil, and meteorological (rainfall intensity) attributes.
- **Inference Pipeline**: Evaluates grid cells across target regions and outputs risk scores (0.0 to 1.0) along with feature importances.
- **Demonstration / Synthetic Datasets**: Generates structured synthetic training data modeling realistic hazard scenarios (landslides/floods) for prototype demonstration.

### 4.5 Shelter Carrying Capacity & Relocation Engine (`backend/app/services/relocation.py` & `ml/`)
- **Carrying Capacity Assessment**: Tracks maximum capacity, current occupancy, available water/food supply days, medical facilities, and structural safety ratings for each shelter.
- **Relocation Optimization**: Constrained optimization model assigning evacuees from affected Red Zones to shelters without exceeding capacity while minimizing total transport distance.

### 4.6 Evacuation Routing Engine (`gis/routing.py`)
- **Hazard-Aware Routing**: Constructs road network graph using NetworkX.
- **Dynamic Weighting**: Edges intersecting Red Zones or high-hazard buffer areas receive heavily inflated cost weights or are blocked entirely. Uses Dijkstra / A* algorithms to compute guaranteed safe routes.

---

## 5. Database Schema (PostGIS)
```
- users (id, email, password_hash, role, created_at)
- hazards (id, name, hazard_type, severity, boundary [Geometry], created_at)
- red_zones (id, hazard_id, risk_level, geometry [Polygon], created_at)
- shelters (id, name, location [Point], max_capacity, current_occupancy, water_supply_days, status, updated_at)
- road_nodes (id, location [Point])
- road_edges (id, source_node, target_node, distance_meters, geometry [LineString], risk_score)
- evacuations (id, origin [Point], shelter_id, route_geometry [LineString], status, timestamp)
```

---

## 6. Offline-First & Deployment Strategy
- **Offline Capabilities**: Service Worker caches map tiles, route GeoJSON responses, emergency contact numbers, and basic instructions in local storage/IndexedDB.
- **Containerized Stack**: Single `docker-compose.yml` orchestrates PostgreSQL/PostGIS, Backend API, ML Pipeline background service, and Frontend React web server.
