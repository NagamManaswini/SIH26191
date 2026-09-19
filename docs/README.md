# SIH26191 — Technical API & Engine Documentation

## 1. Intelligent Relocation Optimization Engine

### Mathematical Optimization Formulation

#### Objective Function
Maximize global relocation suitability $Z$ across population groups $i$ and candidate emergency shelters $j$:

$$Z = \sum_{i} \sum_{j} x_{ij} \cdot S(i, j)$$

where $x_{ij}$ is the integer number of evacuees from population group $i$ assigned to shelter $j$.

#### Suitability Function $S(i, j)$
$$S(i, j) = 0.25 \cdot \text{VulnerabilityRatio}_i + 0.30 \cdot \text{Safety}_j + 0.20 \cdot \text{Resource}_j - 0.15 \cdot \frac{\text{Distance}_{ij}}{\text{MaxDist}} - 0.10 \cdot \text{RouteRisk}_{ij}$$

#### Hard Constraints
1. **Shelter Carrying Capacity Limit**:
   $$\sum_{i} x_{ij} \le \text{AvailableCapacity}_j \quad \forall \text{ shelter } j$$
2. **Population Evacuation Limit**:
   $$\sum_{j} x_{ij} \le \text{TotalPopulation}_i \quad \forall \text{ group } i$$
3. **Non-negativity & Integrality**:
   $$x_{ij} \in \mathbb{Z}_{\ge 0}$$

---

## 2. Dynamic Safe Evacuation Routing Engine

### Graph Construction & Edge Attributes
- Roads are stored as line geometries in PostGIS or GeoJSON network files.
- Nodes represent spatial junction coordinates `(round(lon, 5), round(lat, 5))`.
- Edges carry attributes:
  - `distance_m`: Haversine distance along segment.
  - `hazard_risk`: Spatial intersection (0.0 to 1.0) with active Red/Yellow hazard zone polygons.
  - `accessibility`: Derived from road condition (Good: 1.0, Damaged: 0.4, Flooded: 0.1, Blocked: 0.0).
  - `passable`: Boolean.

### Cost Function & Dijkstra Routing Algorithm
$$\text{Cost}(u, v) = \frac{\text{distance\_m} \times (1.0 + k_{\text{risk}} \cdot \text{hazard\_risk}^2)}{\max(0.2, \text{accessibility})}$$

---

## 3. Shelter Carrying Capacity & Suitability Assessment Engine

### Scoring Formulas
- `maximum_capacity` = shelter.capacity
- `current_occupancy` = shelter.current_occupancy
- `available_capacity` = max(0, maximum_capacity - current_occupancy)
- `occupancy_percentage` = (current_occupancy / maximum_capacity) * 100.0
