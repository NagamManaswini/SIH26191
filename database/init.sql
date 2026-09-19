-- PostgreSQL + PostGIS Initialization Script for SIH26191 Platform

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'public',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. Locations Table
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district VARCHAR(255),
    state VARCHAR(255),
    coordinates GEOMETRY(Point, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_locations_coords ON locations USING GIST(coordinates);

-- 3. Population Table
CREATE TABLE IF NOT EXISTS population (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    total_population INTEGER NOT NULL,
    vulnerable_population INTEGER DEFAULT 0,
    density_per_sq_km DOUBLE PRECISION DEFAULT 0.0,
    area_geometry GEOMETRY(Polygon, 4326),
    location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 4. Shelters Table
CREATE TABLE IF NOT EXISTS shelters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    capacity INTEGER NOT NULL,
    current_occupancy INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    contact_number VARCHAR(50),
    location GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_shelters_location ON shelters USING GIST(location);

-- 5. Shelter Resources Table
CREATE TABLE IF NOT EXISTS shelter_resources (
    id SERIAL PRIMARY KEY,
    shelter_id INTEGER UNIQUE NOT NULL REFERENCES shelters(id) ON DELETE CASCADE,
    water_supply_days DOUBLE PRECISION DEFAULT 0.0,
    food_supply_days DOUBLE PRECISION DEFAULT 0.0,
    medical_kits INTEGER DEFAULT 0,
    power_backup BOOLEAN DEFAULT FALSE,
    sanitation_facilities INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Roads Table
CREATE TABLE IF NOT EXISTS roads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    road_type VARCHAR(100) DEFAULT 'primary',
    condition VARCHAR(100) DEFAULT 'good',
    passable BOOLEAN DEFAULT TRUE,
    path GEOMETRY(LineString, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_roads_path ON roads USING GIST(path);

-- 7. Hazard Zones Table
CREATE TABLE IF NOT EXISTS hazard_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hazard_type VARCHAR(100) NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    risk_score DOUBLE PRECISION DEFAULT 0.0,
    boundary GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_hazard_zones_boundary ON hazard_zones USING GIST(boundary);

-- 8. Rainfall Records Table
CREATE TABLE IF NOT EXISTS rainfall_records (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    rainfall_mm DOUBLE PRECISION NOT NULL,
    duration_hours DOUBLE PRECISION DEFAULT 24.0,
    intensity VARCHAR(50) DEFAULT 'moderate',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    station_location GEOMETRY(Point, 4326)
);

-- 9. Disaster Events Table
CREATE TABLE IF NOT EXISTS disaster_events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    affected_area GEOMETRY(Polygon, 4326),
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 10. Evacuation Routes Table
CREATE TABLE IF NOT EXISTS evacuation_routes (
    id SERIAL PRIMARY KEY,
    route_name VARCHAR(255) NOT NULL,
    origin_location GEOMETRY(Point, 4326) NOT NULL,
    destination_shelter_id INTEGER REFERENCES shelters(id) ON DELETE SET NULL,
    route_path GEOMETRY(LineString, 4326) NOT NULL,
    distance_km DOUBLE PRECISION DEFAULT 0.0,
    estimated_travel_time_mins DOUBLE PRECISION DEFAULT 0.0,
    is_safe BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Relocation Assignments Table
CREATE TABLE IF NOT EXISTS relocation_assignments (
    id SERIAL PRIMARY KEY,
    disaster_event_id INTEGER REFERENCES disaster_events(id) ON DELETE SET NULL,
    source_location_name VARCHAR(255) NOT NULL,
    shelter_id INTEGER REFERENCES shelters(id) ON DELETE CASCADE,
    assigned_population_count INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'assigned',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 12. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    alert_level VARCHAR(50) DEFAULT 'WARNING',
    target_area GEOMETRY(Polygon, 4326),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
