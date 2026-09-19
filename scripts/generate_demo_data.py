"""Script to generate synthetic demo datasets for SIH26191 GIS Hazard Analysis.

Generates:
1. elevation: GeoTIFF & GeoJSON grid
2. slope: GeoTIFF & GeoJSON grid
3. rainfall: GeoJSON station points & CSV records
4. soil: GeoJSON polygons
5. land-use/land-cover: GeoJSON polygons
6. roads: GeoJSON LineStrings
7. population: GeoJSON Polygons
8. shelters: GeoJSON Points
9. historical disaster events: GeoJSON Points & Polygons
"""

import os
import json
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon, LineString, mapping


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "demo")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def generate_raster_and_grids():
    """Generate elevation DEM and slope rasters/grids using numpy and rasterio if available."""
    ensure_data_dir()
    
    min_lon, min_lat = 72.85, 19.05
    max_lon, max_lat = 72.95, 19.15
    rows, cols = 50, 50
    
    lons = np.linspace(min_lon, max_lon, cols)
    lats = np.linspace(min_lat, max_lat, rows)
    
    # Generate synthetic elevation (hills in northeast, valley in southwest)
    xx, yy = np.meshgrid(lons, lats)
    elevation_data = (
        200.0
        + 800.0 * np.sin((xx - min_lon) * 20.0) * np.cos((yy - min_lat) * 20.0)
        + 500.0 * (xx - min_lon) / (max_lon - min_lon) * (yy - min_lat) / (max_lat - min_lat)
    )
    elevation_data = np.clip(elevation_data, 50.0, 1500.0)
    
    # Calculate gradient / slope (degrees)
    dy, dx = np.gradient(elevation_data, 100.0)  # ~100m grid cell resolution
    slope_data = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
    slope_data = np.clip(slope_data, 0.0, 65.0)

    # Save DEM GeoTIFF if rasterio is present
    try:
        import rasterio
        from rasterio.transform import from_bounds
        
        transform = from_bounds(min_lon, min_lat, max_lon, max_lat, cols, rows)
        
        dem_path = os.path.join(DATA_DIR, "elevation_dem.tif")
        with rasterio.open(
            dem_path,
            "w",
            driver="GTiff",
            height=rows,
            width=cols,
            count=1,
            dtype=elevation_data.dtype,
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(elevation_data, 1)

        slope_path = os.path.join(DATA_DIR, "slope_grid.tif")
        with rasterio.open(
            slope_path,
            "w",
            driver="GTiff",
            height=rows,
            width=cols,
            count=1,
            dtype=slope_data.dtype,
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(slope_data, 1)
    except Exception as e:
        print(f"Notice: GeoTIFF write notice: {e}")

    # Also save grid cells as GeoJSON for easy vector visualization
    grid_features = []
    d_lon = (max_lon - min_lon) / cols
    d_lat = (max_lat - min_lat) / rows

    for r in range(rows - 1):
        for c in range(cols - 1):
            x1, y1 = lons[c], lats[r]
            x2, y2 = lons[c + 1], lats[r + 1]
            poly = Polygon([[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]])
            
            elev_val = float(elevation_data[r, c])
            slope_val = float(slope_data[r, c])
            
            grid_features.append(
                {
                    "type": "Feature",
                    "geometry": mapping(poly),
                    "properties": {
                        "cell_id": f"cell_{r}_{c}",
                        "elevation_m": round(elev_val, 2),
                        "slope_deg": round(slope_val, 2),
                    },
                }
            )

    geojson_grid = {"type": "FeatureCollection", "features": grid_features}
    with open(os.path.join(DATA_DIR, "elevation_slope_grid.geojson"), "w") as f:
        json.dump(geojson_grid, f, indent=2)


def generate_vector_datasets():
    ensure_data_dir()

    # 1. Rainfall Stations GeoJSON & CSV
    rainfall_stations = [
        {"name": "Station North Hill", "lon": 72.93, "lat": 19.14, "rainfall_mm": 240.0, "intensity": "extreme"},
        {"name": "Station Central Valley", "lon": 72.89, "lat": 19.10, "rainfall_mm": 115.0, "intensity": "heavy"},
        {"name": "Station South Coast", "lon": 72.86, "lat": 19.06, "rainfall_mm": 60.0, "intensity": "moderate"},
        {"name": "Station East Ridge", "lon": 72.94, "lat": 19.08, "rainfall_mm": 190.0, "intensity": "heavy"},
    ]
    rain_features = [
        {
            "type": "Feature",
            "geometry": mapping(Point(s["lon"], s["lat"])),
            "properties": s,
        }
        for s in rainfall_stations
    ]
    with open(os.path.join(DATA_DIR, "rainfall_stations.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": rain_features}, f, indent=2)

    pd.DataFrame(rainfall_stations).to_csv(os.path.join(DATA_DIR, "rainfall_records.csv"), index=False)

    # 2. Soil Polygons GeoJSON
    soil_zones = [
        {
            "soil_type": "weathered_granite",
            "erodibility_index": 0.85,
            "coords": [[72.90, 19.10], [72.95, 19.10], [72.95, 19.15], [72.90, 19.15], [72.90, 19.10]],
        },
        {
            "soil_type": "sandy_clay_alluvium",
            "erodibility_index": 0.45,
            "coords": [[72.85, 19.05], [72.90, 19.05], [72.90, 19.10], [72.85, 19.10], [72.85, 19.05]],
        },
    ]
    soil_features = [
        {
            "type": "Feature",
            "geometry": mapping(Polygon(z["coords"])),
            "properties": {"soil_type": z["soil_type"], "erodibility_index": z["erodibility_index"]},
        }
        for z in soil_zones
    ]
    with open(os.path.join(DATA_DIR, "soil_polygons.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": soil_features}, f, indent=2)

    # 3. Land Use / Land Cover GeoJSON
    lulc_zones = [
        {
            "land_cover": "steep_barren_slope",
            "runoff_factor": 0.90,
            "coords": [[72.91, 19.11], [72.95, 19.11], [72.95, 19.15], [72.91, 19.15], [72.91, 19.11]],
        },
        {
            "land_cover": "dense_forest",
            "runoff_factor": 0.25,
            "coords": [[72.85, 19.08], [72.90, 19.08], [72.90, 19.13], [72.85, 19.13], [72.85, 19.08]],
        },
    ]
    lulc_features = [
        {
            "type": "Feature",
            "geometry": mapping(Polygon(z["coords"])),
            "properties": {"land_cover": z["land_cover"], "runoff_factor": z["runoff_factor"]},
        }
        for z in lulc_zones
    ]
    with open(os.path.join(DATA_DIR, "land_use.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": lulc_features}, f, indent=2)

    # 4. Roads GeoJSON
    roads = [
        {
            "name": "State Highway 12",
            "road_type": "highway",
            "condition": "good",
            "coords": [[72.86, 19.06], [72.89, 19.09], [72.92, 19.12], [72.94, 19.14]],
        },
        {
            "name": "Mountain Ridge Road",
            "road_type": "secondary",
            "condition": "damaged",
            "coords": [[72.90, 19.10], [72.92, 19.11], [72.95, 19.13]],
        },
    ]
    road_features = [
        {
            "type": "Feature",
            "geometry": mapping(LineString(r["coords"])),
            "properties": {"name": r["name"], "road_type": r["road_type"], "condition": r["condition"]},
        }
        for r in roads
    ]
    with open(os.path.join(DATA_DIR, "roads_network.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": road_features}, f, indent=2)

    # 5. Population Sectors GeoJSON
    sectors = [
        {
            "name": "Ward 1 Riverside",
            "population": 14200,
            "vulnerable": 2100,
            "coords": [[72.86, 19.06], [72.89, 19.06], [72.89, 19.09], [72.86, 19.09], [72.86, 19.06]],
        },
        {
            "name": "Ward 2 North Foothills",
            "population": 8500,
            "vulnerable": 1200,
            "coords": [[72.90, 19.11], [72.94, 19.11], [72.94, 19.14], [72.90, 19.14], [72.90, 19.11]],
        },
    ]
    pop_features = [
        {
            "type": "Feature",
            "geometry": mapping(Polygon(s["coords"])),
            "properties": {"location_name": s["name"], "total_population": s["population"], "vulnerable_population": s["vulnerable"]},
        }
        for s in sectors
    ]
    with open(os.path.join(DATA_DIR, "population_sectors.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": pop_features}, f, indent=2)

    # 6. Shelters GeoJSON
    shelters = [
        {"name": "Central High School Relief Shelter", "lon": 72.87, "lat": 19.07, "capacity": 500, "status": "active"},
        {"name": "North Ridge Community Stadium", "lon": 72.92, "lat": 19.13, "capacity": 1200, "status": "active"},
    ]
    shelter_features = [
        {
            "type": "Feature",
            "geometry": mapping(Point(s["lon"], s["lat"])),
            "properties": s,
        }
        for s in shelters
    ]
    with open(os.path.join(DATA_DIR, "shelters.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": shelter_features}, f, indent=2)

    # 7. Historical Disaster Events GeoJSON
    events = [
        {
            "title": "2023 Monsoon Landslide Alpha",
            "type": "landslide",
            "severity": "CRITICAL",
            "year": 2023,
            "coords": [[72.92, 19.12], [72.95, 19.12], [72.95, 19.15], [72.92, 19.15], [72.92, 19.12]],
        },
        {
            "title": "2024 Flash Flood Catchment",
            "type": "flood",
            "severity": "HIGH",
            "year": 2024,
            "coords": [[72.86, 19.06], [72.89, 19.06], [72.89, 19.08], [72.86, 19.08], [72.86, 19.06]],
        },
    ]
    event_features = [
        {
            "type": "Feature",
            "geometry": mapping(Polygon(e["coords"])),
            "properties": {"title": e["title"], "event_type": e["type"], "severity": e["severity"], "year": e["year"]},
        }
        for e in events
    ]
    with open(os.path.join(DATA_DIR, "historical_disasters.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": event_features}, f, indent=2)


if __name__ == "__main__":
    generate_raster_and_grids()
    generate_vector_datasets()
    print("Successfully generated all synthetic demo datasets in data/demo/")
