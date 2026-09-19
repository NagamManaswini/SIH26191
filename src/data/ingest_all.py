"""Master Orchestrator, PostGIS Database Seeder & Verification Runner."""

import sys
import os
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import geopandas as gpd
import pandas as pd

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Import data pipeline modules
from src.data.elevation_pipeline import clip_and_export_terrain, DEFAULT_BBOX
from src.data.hazard_inventory import fetch_historical_hazard_inventory
from src.data.weather_feed import fetch_live_weather_feed
from src.data.demographics_pipeline import load_demographics_grid
from src.data.infrastructure_loader import load_shelter_infrastructure, download_road_network_graph, fetch_admin_boundaries

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:sql123@localhost:5432/servers")


def get_db_engine():
    """Create SQLAlchemy engine for PostgreSQL/PostGIS database."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def seed_spatial_tables(engine):
    """Create spatial tables in PostgreSQL/PostGIS and seed ingested data."""
    print("\n--- 1. Initializing Spatial Tables in PostgreSQL ---")
    
    with engine.begin() as conn:
        # Drop and recreate tables cleanly
        conn.execute(text("DROP TABLE IF EXISTS hazards_redzone CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS shelters_capacity CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS population_clusters CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS road_network CASCADE;"))

        # Create table schemas matching dataframe fields
        conn.execute(text("""
            CREATE TABLE hazards_redzone (
                id SERIAL PRIMARY KEY,
                disaster_type VARCHAR(100),
                source VARCHAR(255),
                district VARCHAR(100),
                state VARCHAR(100),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                trigger_rainfall_mm_day DOUBLE PRECISION,
                soil_type VARCHAR(100),
                slope_deg DOUBLE PRECISION,
                risk_label VARCHAR(50),
                fatality_count INT,
                event_date VARCHAR(50),
                geometry TEXT
            );

            CREATE TABLE shelters_capacity (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                type VARCHAR(100),
                district VARCHAR(100),
                locality VARCHAR(100),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                max_capacity INT,
                current_occupancy INT,
                available_capacity INT,
                has_medical_facility BOOLEAN,
                has_power_backup BOOLEAN,
                water_supply_liters INT,
                geometry TEXT
            );

            CREATE TABLE population_clusters (
                id SERIAL PRIMARY KEY,
                cluster_id VARCHAR(100),
                district VARCHAR(100),
                locality VARCHAR(100),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                total_population INT,
                area_sq_km DOUBLE PRECISION,
                children_under_5_pct DOUBLE PRECISION,
                elderly_over_65_pct DOUBLE PRECISION,
                disabled_pct DOUBLE PRECISION,
                pop_density_per_sq_km DOUBLE PRECISION,
                children_headcount INT,
                elderly_headcount INT,
                vulnerable_headcount INT,
                geometry TEXT
            );

            CREATE TABLE road_network (
                id SERIAL PRIMARY KEY,
                road_id VARCHAR(100),
                name VARCHAR(255),
                road_type VARCHAR(100),
                speed_limit_kmh INT,
                lane_count INT,
                geometry TEXT
            );
        """))
    print("[OK] Created database tables: hazards_redzone, shelters_capacity, population_clusters, road_network.")


def run_ingestion_pipeline():
    """Execute all pipeline modules and seed database tables."""
    start_time = time.time()
    print("==================================================================")
    print("  SIH26191 CORE GEOSPATIAL DATASETS INGESTION & SEEDING PIPELINE  ")
    print("==================================================================")
    print(f"Target Database URL: {DATABASE_URL.split('@')[-1]}")

    engine = get_db_engine()
    seed_spatial_tables(engine)

    summary_rows = []

    # Step 1: Elevation Terrain Pipeline
    print("\n--- [Step 1/5] Ingesting Elevation & Terrain Metrics ---")
    terrain_info = clip_and_export_terrain(DEFAULT_BBOX)
    summary_rows.append({
        "layer_name": "NASA SRTM DEM Terrain",
        "records_ingested": 1,
        "spatial_coverage": f"BBOX {DEFAULT_BBOX}",
        "status": "SUCCESS",
    })

    # Step 2: Historical Hazard Inventory
    print("\n--- [Step 2/5] Ingesting ISRO Landslide Atlas & INDOFLOODS ---")
    hazards_gdf = fetch_historical_hazard_inventory()
    hazards_gdf["geometry"] = hazards_gdf["geometry"].astype(str)
    hazards_df = pd.DataFrame(hazards_gdf)
    hazards_df.to_sql("hazards_redzone", con=engine, if_exists="append", index=False)
    print(f"[OK] Seeded {len(hazards_df)} hazard inventory records into 'hazards_redzone'.")
    summary_rows.append({
        "layer_name": "ISRO Landslide Atlas / INDOFLOODS",
        "records_ingested": len(hazards_df),
        "spatial_coverage": "India (Kerala, Himachal, Uttarakhand)",
        "status": "SUCCESS",
    })

    # Step 3: High-Resolution Demographics
    print("\n--- [Step 3/5] Ingesting WorldPop 100m & Meta HRSL Demographics ---")
    pop_gdf = load_demographics_grid()
    pop_gdf["geometry"] = pop_gdf["geometry"].astype(str)
    pop_df = pd.DataFrame(pop_gdf)
    pop_df.to_sql("population_clusters", con=engine, if_exists="append", index=False)
    print(f"[OK] Seeded {len(pop_df)} population cluster records into 'population_clusters'.")
    summary_rows.append({
        "layer_name": "WorldPop / Meta HRSL Demographics",
        "records_ingested": len(pop_df),
        "spatial_coverage": "Western Ghats Red Zone Clusters",
        "status": "SUCCESS",
    })

    # Step 4: Safe-Haven Shelters Infrastructure
    print("\n--- [Step 4/5] Ingesting OSM Shelters Infrastructure ---")
    shelters_gdf = load_shelter_infrastructure()
    shelters_gdf["geometry"] = shelters_gdf["geometry"].astype(str)
    shelters_df = pd.DataFrame(shelters_gdf)
    shelters_df.to_sql("shelters_capacity", con=engine, if_exists="append", index=False)
    print(f"[OK] Seeded {len(shelters_df)} shelter records into 'shelters_capacity'.")
    summary_rows.append({
        "layer_name": "OSM Safe-Haven Shelters",
        "records_ingested": len(shelters_df),
        "spatial_coverage": "Wayanad / Kerala Districts",
        "status": "SUCCESS",
    })

    # Step 5: Road Network Graph
    print("\n--- [Step 5/5] Ingesting Evacuation Road Network Graph ---")
    roads_gdf = download_road_network_graph()
    roads_gdf["geometry"] = roads_gdf["geometry"].astype(str)
    road_cols = [c for c in ["road_id", "name", "road_type", "speed_limit_kmh", "lane_count", "geometry"] if c in roads_gdf.columns]
    roads_df = pd.DataFrame(roads_gdf[road_cols])
    roads_df.to_sql("road_network", con=engine, if_exists="append", index=False)
    print(f"[OK] Seeded {len(roads_df)} road network segments into 'road_network'.")
    summary_rows.append({
        "layer_name": "OSM Evacuation Road Network",
        "records_ingested": len(roads_df),
        "spatial_coverage": "Wayanad Regional Drive Graph",
        "status": "SUCCESS",
    })

    elapsed = round(time.time() - start_time, 2)

    # Output Final Execution Summary Report
    print("\n==================================================================")
    print("                INGESTION EXECUTION SUMMARY REPORT                ")
    print("==================================================================")
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    print("------------------------------------------------------------------")
    print(f"Total Execution Time: {elapsed} seconds")
    print("All core geospatial datasets successfully integrated and seeded into PostgreSQL!")
    print("==================================================================\n")
    return summary_df


if __name__ == "__main__":
    run_ingestion_pipeline()
