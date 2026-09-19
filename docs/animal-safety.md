# Feature 3 — Animal Safety Module

## Overview
The Animal Safety Module addresses a major evacuation challenge: citizens hesitating to evacuate because of concern for livestock, pets, and property. This module tracks registered animals, manages dedicated animal shelters, and generates optimized animal rescue plans with **strict capacity separation from human relief shelters**.

---

## Database Architecture

### `Animal` Table
- `id`: Integer Primary Key
- `tag_id`: String (Unique Tag / RFID / Barcode)
- `owner_id`: String (Owner citizen ID / Cooperative ID)
- `owner_name`: String (Owner full name)
- `animal_type`: Enum (`cattle`, `goats`, `sheep`, `dogs`, `cats`, `poultry`, `other_livestock`)
- `name`: String (Herd label or pet name)
- `location_name`: String (Current location sector)
- `emergency_status`: Enum (`SAFE`, `AT_RISK`, `EVACUATING`, `RELOCATED`)
- `rescue_status`: Enum (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `UNASSIGNED`)
- `destination_shelter_id`: Foreign Key (`animal_shelters.id`)

### `AnimalShelter` Table
- `id`: Integer Primary Key
- `name`: Facility Name
- `address`: Address / Location
- `capacity`: Integer (Total animal capacity)
- `current_occupancy`: Integer (Occupied spaces)
- `supported_animal_types`: String CSV (`cattle,goats,sheep,dogs,cats,poultry`)
- `water_availability`: Boolean
- `food_availability`: Boolean
- `safety_status`: Enum (`SAFE`, `AT_RISK`, `INUNDATED`)

> [!IMPORTANT]
> Human shelter capacity (`shelters` table) and animal shelter capacity (`animal_shelters` table) are maintained in separate database entities to prevent capacity mixing and maintain hygiene standards.

---

## REST APIs
- `POST /api/v1/animals`: Register animal or livestock herd.
- `GET /api/v1/animals`: List animals (filtered by status or type).
- `GET /api/v1/animals/{id}`: Get animal details.
- `PATCH /api/v1/animals/{id}`: Update emergency status or destination shelter.
- `GET /api/v1/animals/shelters`: List dedicated animal shelters and available capacity.
- `POST /api/v1/animals/shelters`: Create animal shelter.
- `POST /api/v1/animals/rescue-plan`: Run rescue optimizer mapping Red Zone animals to Animal Shelters.

---

## Implementation Status
- [x] **IMPLEMENTED**: Animal & AnimalShelter database entities & ORM models
- [x] **IMPLEMENTED**: Animal Safety REST APIs & CRUD services
- [x] **IMPLEMENTED**: Animal Rescue Optimizer engine
- [x] **IMPLEMENTED**: Frontend Animal Safety Command Dashboard (`AnimalSafetyPage.tsx`)
- [ ] **FUTURE INTEGRATION**: RFID / Bluetooth Ear Tag hardware scanner integration
