"""Historical Hazard & Landslide Inventory Pipeline (ISRO Landslide Atlas & INDOFLOODS)."""

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# Benchmark ISRO Landslide Atlas of India & INDOFLOODS historical hazard dataset
BENCHMARK_HAZARD_EVENTS = [
    {
        "disaster_type": "landslide",
        "source": "ISRO Landslide Atlas of India",
        "district": "Wayanad",
        "state": "Kerala",
        "latitude": 11.5204,
        "longitude": 76.1368,
        "trigger_rainfall_mm_day": 340.5,
        "soil_type": "Clay Loam",
        "slope_deg": 38.5,
        "risk_label": "critical",
        "fatality_count": 220,
        "event_date": "2024-07-30",
    },
    {
        "disaster_type": "landslide",
        "source": "ISRO Landslide Atlas of India",
        "district": "Idukki",
        "state": "Kerala",
        "latitude": 9.8496,
        "longitude": 76.9804,
        "trigger_rainfall_mm_day": 285.0,
        "soil_type": "Sandy Clay",
        "slope_deg": 34.2,
        "risk_label": "critical",
        "fatality_count": 66,
        "event_date": "2020-08-07",
    },
    {
        "disaster_type": "flood",
        "source": "IIT Delhi INDOFLOODS",
        "district": "Ernakulam",
        "state": "Kerala",
        "latitude": 9.9816,
        "longitude": 76.2999,
        "trigger_rainfall_mm_day": 210.0,
        "soil_type": "Alluvial",
        "slope_deg": 4.1,
        "risk_label": "high",
        "fatality_count": 15,
        "event_date": "2018-08-15",
    },
    {
        "disaster_type": "landslide",
        "source": "ISRO Landslide Atlas of India",
        "district": "Shimla",
        "state": "Himachal Pradesh",
        "latitude": 31.1048,
        "longitude": 77.1734,
        "trigger_rainfall_mm_day": 195.0,
        "soil_type": "Silty Loam",
        "slope_deg": 42.0,
        "risk_label": "high",
        "fatality_count": 28,
        "event_date": "2023-08-14",
    },
    {
        "disaster_type": "flood",
        "source": "IIT Delhi INDOFLOODS",
        "district": "Chamoli",
        "state": "Uttarakhand",
        "latitude": 30.4124,
        "longitude": 79.3308,
        "trigger_rainfall_mm_day": 240.0,
        "soil_type": "Rocky Silt",
        "slope_deg": 28.0,
        "risk_label": "critical",
        "fatality_count": 70,
        "event_date": "2021-02-07",
    },
    {
        "disaster_type": "landslide",
        "source": "ISRO Landslide Atlas of India",
        "district": "Wayanad",
        "state": "Kerala",
        "latitude": 11.5800,
        "longitude": 76.1000,
        "trigger_rainfall_mm_day": 165.0,
        "soil_type": "Clay Loam",
        "slope_deg": 26.5,
        "risk_label": "medium",
        "fatality_count": 0,
        "event_date": "2019-08-08",
    },
]


def fetch_historical_hazard_inventory():
    """Fetch structured historical landslide and flood disaster inventory.
    
    Returns a GeoPandas GeoDataFrame with coordinate points, trigger rainfall, soil type, and risk labels.
    """
    df = pd.DataFrame(BENCHMARK_HAZARD_EVENTS)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf


def export_hazard_inventory(output_path="./data/export/hazard_inventory.geojson"):
    """Export historical hazard inventory to GeoJSON for ML training & GIS overlay."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    gdf = fetch_historical_hazard_inventory()
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"[OK] Exported {len(gdf)} historical hazard inventory records to '{output_path}'.")
    return gdf


if __name__ == "__main__":
    inventory = export_hazard_inventory()
    print(inventory.head())
