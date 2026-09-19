# SIH26191 — Comprehensive Geospatial Datasets Reference Guide

This document lists all core free datasets integrated into the **SIH26191 Intelligent Disaster Management Platform**, detailing their source URLs, spatial resolution, update frequency, and access method (Automated API/GEE vs. Manual Download).

---

## 🛰️ Master Dataset Inventory

| # | Dataset Name | Category | Provider / Source URL | Spatial Resolution | Update Frequency | Access Method | Status |
|---|---|---|---|---|---|---|---|
| **1** | **NASA/USGS SRTM 30m DEM** | Elevation / Terrain | [USGS / NASA GEE](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) | 30m Grid | Static Baseline | Automated GEE / Engine | ✓ Live |
| **2** | **NASADEM 12.5m Radar DEM** | Radar Elevation | [NASA GEE](https://developers.google.com/earth-engine/datasets/catalog/NASA_NASADEM_HGT_001) | 12.5m Grid | Static Baseline | Automated GEE / Engine | ✓ Live |
| **3** | **ISRO CartoDEM** | High-Res Terrain | [ISRO Bhuvan Portal](https://bhuvan-app3.nrsc.gov.in/data/download/index.php) | 10m / 30m | Periodic Updates | Manual Download (`./data/raw/cartodem/`) | ✓ Local/Stub |
| **4** | **Sentinel-2 Multi-Spectral** | Satellite Imagery | [Copernicus GEE](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED) | 10m Bands | 5-Day Revisit | Automated GEE / Engine | ✓ Live |
| **5** | **ESRI 10m Annual LULC** | Land Use / Land Cover | [ESRI / Impact Observatory GEE](https://projects.planet.com/) | 10m Grid | Annual | Automated GEE / Engine | ✓ Live |
| **6** | **Google Dynamic World 10m** | Real-Time LULC | [Google Dynamic World GEE](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1) | 10m Grid | Near Real-Time (Daily) | Automated GEE / Engine | ✓ Live |
| **7** | **Global Forest Watch** | Tree Loss / Gain | [UMD / Hansen GEE](https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2023_v1_11) | 30m Grid | Annual | Automated GEE / Engine | ✓ Live |
| **8** | **WorldPop 100m Grid** | Demographics | [WorldPop / GEE](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop) | 100m Grid | Annual | Automated GEE / Engine | ✓ Live |
| **9** | **Meta HRSL 30m** | Demographics | [Meta / HDX HumData](https://data.humdata.org/dataset/meta-high-resolution-settlement-layer-hrsl) | 30m Grid | Periodic | Automated HDX / Local (`./data/raw/hrsl/`) | ✓ Live |
| **10** | **DataMeet India Boundaries** | Administrative Vector | [DataMeet GitHub](https://github.com/datameet/maps) | Vector Polygons | Annual | Automated GitHub Download | ✓ Live |
| **11** | **OpenStreetMap Road Network** | Infrastructure & Roads | [OpenStreetMap via OSMnx](https://osmnx.readthedocs.io/) | Vector Graph | Real-Time Edits | Automated OSMnx API | ✓ Live |
| **12** | **Overpass Shelter Infrastructure** | Safe-Haven Shelters | [Overpass API](https://overpass-api.de/) | Point Features | Real-Time Edits | Automated Overpass API | ✓ Live |
| **13** | **Geofabrik India OSM Extract** | Road Network Graph | [Geofabrik GmbH](https://download.geofabrik.de/asia/india.html) | Regional PBF | Daily Updates | `osm2pgrouting` Wrapper | ✓ Live |
| **14** | **Open-Meteo Weather API** | Weather & Hydrology | [Open-Meteo API](https://open-meteo.com/) | 1km Grid | Hourly / 7-Day | Automated REST API (No Key) | ✓ Live |
| **15** | **IMD Open Data Rainfall** | Daily Rainfall Grid | [IMD CDSP Portal](https://cdsp.imdpune.gov.in/) | 0.25° Grid | Daily | Manual Download (`./data/raw/imd_rainfall/`) | ✓ Stub Active |
| **16** | **ECMWF ERA5-Land** | Climate Reanalysis | [ECMWF GEE](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_HOURLY) | 9km Grid | Hourly / Historical | Automated GEE / Engine | ✓ Live |
| **17** | **ISRIC SoilGrids 250m** | Soil Depth & Texture | [ISRIC World Soil Information](https://rest.isric.org/) | 250m Grid | Static | Automated REST API | ✓ Live |
| **18** | **IITD ISED/IWED Soil Erosion** | Soil Erodibility | [IIT Delhi HydroSense](https://hydrosense.iitd.ac.in/) | Regional Map | Static | Manual Download (`./data/raw/soil_erosion/`) | ✓ Stub Active |
| **19** | **ISRO Landslide Atlas** | Hazard History | [ISRO Bhuvan Portal](https://bhuvan-app3.nrsc.gov.in/landslide/) | Point / Polygon | Event-Driven | Local CSV / Shapefile | ✓ Live |
| **20** | **INDOFLOODS Flood Inventory** | Flood History | [IIT Delhi INDOFLOODS](https://hydrosense.iitd.ac.in/) | Event Records | Historical | Local CSV / Shapefile | ✓ Live |
| **21** | **EM-DAT Disaster Database** | Natural Disasters | [CRED EM-DAT / KaggleHub](https://www.emdat.be/) | Global Country | Event-Driven | Automated `kagglehub` API | ✓ Live |
| **22** | **NASA FIRMS Fire Alerts** | Thermal Anomaly | [NASA FIRMS API](https://firms.modaps.eosdis.nasa.gov/) | 375m VIIRS | Real-Time (3-Hour) | Automated REST API | ✓ Live |
| **23** | **JRC Global Surface Water** | Surface Water Extent | [EC JRC GEE](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater) | 30m Grid | 40-Year Record | Automated GEE / Engine | ✓ Live |
| **24** | **Mission Antyodaya** | Village Infrastructure | [data.gov.in Portal](https://data.gov.in/) | Panchayat Level | Annual | Automated API / Benchmark | ✓ Live |

---

## 🗄️ PostgreSQL / PostGIS Seeder Mapping

When `python src/data/main_pipeline.py` is executed, the following spatial tables are populated in PostgreSQL:

1. **`hazards_redzone`**: ISRO Landslide Atlas + INDOFLOODS + NASA FIRMS records
2. **`shelters_capacity`**: OSMnx shelters + Mission Antyodaya panchayat infrastructure
3. **`population_clusters`**: WorldPop 100m grid + Meta HRSL 30m demographics
4. **`soil_erosion`**: ISRIC SoilGrids 250m + IITD ISED/IWED erodibility metrics
5. **`flood_history`**: INDOFLOODS + JRC Surface Water inundation records
6. **`landslide_history`**: ISRO Landslide Atlas historical landslides
