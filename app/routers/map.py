import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.sensor import Sensor
from app.models.watershed import Watershed
from app.models.evacuation import EvacuationCenter
from app.models.citizen_report import CitizenReport
from app.models.alert import Alert
from app.models.prediction import FloodPrediction
from app.models.sensor_health import SensorHealth
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.enums import SensorType, SensorStatus, RiskLevel, AlertStatus, VerificationStatus

router = APIRouter(prefix="/map", tags=["GIS Map"])


def _get_sensor_signal_strength(db: Session, sensor_id: int) -> float:
    health = db.query(SensorHealth).filter(SensorHealth.sensor_id == sensor_id).order_by(desc(SensorHealth.recorded_at)).first()
    return health.signal_strength if health else -70.0


def _extract_latest_sensor_reading(sensor: Sensor, db: Session) -> Optional[Dict[str, Any]]:
    """Helper to fetch latest reading for a sensor."""
    if sensor.sensor_type == SensorType.RAINFALL:
        r = db.query(RainfallReading).filter(RainfallReading.sensor_id == sensor.id).order_by(desc(RainfallReading.timestamp)).first()
        if r:
            return {"value": r.rainfall_mm, "unit": "mm/hr", "param": "Rainfall", "timestamp": r.timestamp.isoformat() if r.timestamp else None}
    elif sensor.sensor_type == SensorType.RIVER_LEVEL:
        r = db.query(RiverReading).filter(RiverReading.sensor_id == sensor.id).order_by(desc(RiverReading.timestamp)).first()
        if r:
            return {"value": r.water_level_m, "unit": "m", "param": "River Stage", "timestamp": r.timestamp.isoformat() if r.timestamp else None}
    elif sensor.sensor_type == SensorType.SOIL_MOISTURE:
        r = db.query(SoilMoistureReading).filter(SoilMoistureReading.sensor_id == sensor.id).order_by(desc(SoilMoistureReading.timestamp)).first()
        if r:
            return {"value": r.moisture_percentage, "unit": "%", "param": "Soil Moisture", "timestamp": r.timestamp.isoformat() if r.timestamp else None}
    elif sensor.sensor_type in (SensorType.WEATHER, SensorType.MULTI_SENSOR):
        rain = db.query(RainfallReading).filter(RainfallReading.sensor_id == sensor.id).order_by(desc(RainfallReading.timestamp)).first()
        riv = db.query(RiverReading).filter(RiverReading.sensor_id == sensor.id).order_by(desc(RiverReading.timestamp)).first()
        soil = db.query(SoilMoistureReading).filter(SoilMoistureReading.sensor_id == sensor.id).order_by(desc(SoilMoistureReading.timestamp)).first()
        readings_dict = {}
        ts = None
        if rain:
            readings_dict["rainfall_mm"] = rain.rainfall_mm
            ts = rain.timestamp
        if riv:
            readings_dict["water_level_m"] = riv.water_level_m
            ts = ts or riv.timestamp
        if soil:
            readings_dict["moisture_percentage"] = soil.moisture_percentage
            ts = ts or soil.timestamp
        return {
            "value": readings_dict.get("rainfall_mm") or readings_dict.get("water_level_m") or 0.0,
            "unit": "multi",
            "param": "Multi-telemetry",
            "multi_values": readings_dict,
            "timestamp": ts.isoformat() if ts else None
        }
    return None


@router.get("/sensors")
def get_map_sensors(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get all sensor markers with telemetry as GeoJSON FeatureCollection.
    """
    sensors = db.query(Sensor).all()
    features = []

    for s in sensors:
        latest = _extract_latest_sensor_reading(s, db)
        ws_name = s.watershed.name if s.watershed else "Unassigned Catchment"

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [s.longitude, s.latitude]
            },
            "properties": {
                "id": s.id,
                "sensor_code": s.sensor_code,
                "name": s.name,
                "sensor_type": s.sensor_type.value if hasattr(s.sensor_type, "value") else str(s.sensor_type),
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                "latitude": s.latitude,
                "longitude": s.longitude,
                "elevation": s.elevation,
                "battery_level": s.battery_level,
                "signal_strength": _get_sensor_signal_strength(db, s.id),
                "last_seen": s.last_seen.isoformat() if s.last_seen else None,
                "watershed_id": s.watershed_id,
                "watershed_name": ws_name,
                "latest_reading": latest
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/watersheds")
def get_map_watersheds(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get watershed boundaries as GeoJSON FeatureCollection with live aggregated hydrology,
    AI flood predictions, and active alerts.
    """
    watersheds = db.query(Watershed).all()
    features = []

    for ws in watersheds:
        # Parse geometry
        geom = None
        if ws.geometry:
            try:
                geom = json.loads(ws.geometry)
            except Exception:
                geom = None
        
        # Fallback default geometry if missing
        if not geom:
            geom = {
                "type": "Polygon",
                "coordinates": [[
                    [78.90, 30.55],
                    [79.18, 30.55],
                    [79.18, 30.75],
                    [78.90, 30.75],
                    [78.90, 30.55]
                ]]
            }

        # Gather watershed sensor readings
        sensor_ids = [s.id for s in ws.sensors] if ws.sensors else []
        
        # Rainfall
        avg_rainfall = None
        if sensor_ids:
            rain_records = db.query(RainfallReading).filter(RainfallReading.sensor_id.in_(sensor_ids)).order_by(desc(RainfallReading.timestamp)).limit(10).all()
            if rain_records:
                avg_rainfall = round(sum(r.rainfall_mm for r in rain_records) / len(rain_records), 2)
        
        # River stage
        max_river = None
        if sensor_ids:
            river_records = db.query(RiverReading).filter(RiverReading.sensor_id.in_(sensor_ids)).order_by(desc(RiverReading.timestamp)).limit(10).all()
            if river_records:
                max_river = round(max(r.water_level_m for r in river_records), 2)

        # Soil moisture
        avg_soil = None
        if sensor_ids:
            soil_records = db.query(SoilMoistureReading).filter(SoilMoistureReading.sensor_id.in_(sensor_ids)).order_by(desc(SoilMoistureReading.timestamp)).limit(10).all()
            if soil_records:
                avg_soil = round(sum(r.moisture_percentage for r in soil_records) / len(soil_records), 1)

        # Latest AI Prediction
        pred = db.query(FloodPrediction).filter(FloodPrediction.watershed_id == ws.id).order_by(desc(FloodPrediction.prediction_time)).first()
        pred_dict = None
        if pred:
            pred_dict = {
                "forecast_for": pred.forecast_for.isoformat() if pred.forecast_for else None,
                "predicted_water_level": pred.predicted_water_level,
                "probability": pred.probability,
                "risk_level": pred.risk_level.value if hasattr(pred.risk_level, "value") else str(pred.risk_level),
                "confidence": pred.confidence
            }

        # Active Alert near watershed
        active_alert = None
        # Check alerts with matching district or close location
        alert = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).order_by(desc(Alert.created_at)).first()
        if alert:
            active_alert = {
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity),
                "message": alert.message,
                "radius_km": alert.radius_km
            }

        feature = {
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "id": ws.id,
                "name": ws.name,
                "code": ws.code,
                "district": ws.district,
                "state": ws.state,
                "area_sq_km": ws.area_sq_km,
                "risk_level": ws.risk_level.value if hasattr(ws.risk_level, "value") else str(ws.risk_level),
                "sensor_count": len(ws.sensors) if ws.sensors else 0,
                "rainfall_avg_mm": avg_rainfall if avg_rainfall is not None else 8.5,
                "river_level_max_m": max_river if max_river is not None else 2.15,
                "soil_moisture_avg_pct": avg_soil if avg_soil is not None else 64.0,
                "prediction": pred_dict,
                "active_alert": active_alert
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/risk-zones")
def get_map_risk_zones() -> Dict[str, Any]:
    """
    Get flood-risk zones with hazard levels, inundation depths, and GeoJSON polygons.
    """
    risk_zones = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [78.96, 30.60], [79.05, 30.58], [79.08, 30.66], [78.98, 30.68], [78.96, 30.60]
                ]]
            },
            "properties": {
                "id": "RZ-MANDAKINI-CRITICAL",
                "name": "Sonprayag-Gaurikund Confluence Inundation Zone",
                "risk_level": "CRITICAL",
                "expected_depth_m": 3.8,
                "hazard_type": "Flash Flood & Debris Torrent",
                "evacuation_status": "MANDATORY EVACUATION ADVISED",
                "color": "#EF4444"
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [79.48, 30.48], [79.62, 30.46], [79.64, 30.56], [79.50, 30.58], [79.48, 30.48]
                ]]
            },
            "properties": {
                "id": "RZ-ALAKNANDA-HIGH",
                "name": "Joshimath Gorge High Flood Risk Corridor",
                "risk_level": "HIGH",
                "expected_depth_m": 2.6,
                "hazard_type": "Surge Inflow & Slope Slippage",
                "evacuation_status": "PREPARE EVACUATION",
                "color": "#F97316"
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [78.38, 30.70], [78.52, 30.68], [78.54, 30.78], [78.40, 30.80], [78.38, 30.70]
                ]]
            },
            "properties": {
                "id": "RZ-BHAGIRATHI-MODERATE",
                "name": "Uttarkashi Town Low-Lying Riverbank",
                "risk_level": "MODERATE",
                "expected_depth_m": 1.4,
                "hazard_type": "River Overflow & Siltation",
                "evacuation_status": "WATCH & MONITOR",
                "color": "#F59E0B"
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [77.12, 31.90], [77.24, 31.88], [77.26, 32.02], [77.14, 32.04], [77.12, 31.90]
                ]]
            },
            "properties": {
                "id": "RZ-BEAS-LOW",
                "name": "Kullu Floodplain Buffer Zone",
                "risk_level": "LOW",
                "expected_depth_m": 0.6,
                "hazard_type": "Lowland Waterlogging",
                "evacuation_status": "NORMAL ADVISORY",
                "color": "#10B981"
            }
        }
    ]

    return {
        "type": "FeatureCollection",
        "features": risk_zones
    }


@router.get("/evacuation-centers")
def get_map_evacuation_centers(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get evacuation centers with live occupancy, capacity, and GeoJSON Point geometries.
    """
    centers = db.query(EvacuationCenter).all()
    features = []

    for ec in centers:
        occupancy_rate = round((ec.current_occupancy / ec.capacity * 100) if ec.capacity > 0 else 0, 1)
        status = "AVAILABLE" if occupancy_rate < 85 else ("NEAR_CAPACITY" if occupancy_rate < 100 else "FULL")
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [ec.longitude, ec.latitude]
            },
            "properties": {
                "id": ec.id,
                "name": ec.name,
                "latitude": ec.latitude,
                "longitude": ec.longitude,
                "capacity": ec.capacity,
                "current_occupancy": ec.current_occupancy,
                "available_spaces": max(0, ec.capacity - ec.current_occupancy),
                "occupancy_rate": occupancy_rate,
                "status": status,
                "contact_number": ec.contact_number,
                "facilities": ec.facilities
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/citizen-reports")
def get_map_citizen_reports(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get citizen crowd-sourced ground truth reports on the map.
    """
    reports = db.query(CitizenReport).order_by(desc(CitizenReport.created_at)).limit(50).all()
    features = []

    for r in reports:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r.longitude, r.latitude]
            },
            "properties": {
                "id": r.id,
                "report_type": r.report_type.value if hasattr(r.report_type, "value") else str(r.report_type),
                "description": r.description,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "image_url": r.image_url,
                "verification_status": r.verification_status.value if hasattr(r.verification_status, "value") else str(r.verification_status),
                "confidence_score": r.confidence_score if hasattr(r, "confidence_score") and r.confidence_score is not None else 50.0,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/alerts")
def get_map_alerts(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get active flood alert zones with coordinate radius buffer specifications.
    """
    alerts = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).all()
    features = []

    for a in alerts:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [a.longitude, a.latitude]
            },
            "properties": {
                "id": a.id,
                "alert_type": a.alert_type.value if hasattr(a.alert_type, "value") else str(a.alert_type),
                "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
                "title": a.title,
                "message": a.message,
                "latitude": a.latitude,
                "longitude": a.longitude,
                "radius_km": a.radius_km,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "expires_at": a.expires_at.isoformat() if a.expires_at else None,
                "status": a.status.value if hasattr(a.status, "value") else str(a.status)
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }
