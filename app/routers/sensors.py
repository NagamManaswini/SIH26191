from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sensor import Sensor
from app.models.watershed import Watershed
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.sensor_health import SensorHealth
from app.models.enums import SensorType, SensorStatus
from app.schemas.sensor import (
    SensorRead,
    SensorCreate,
    SensorUpdate,
    SensorHealthOverview,
    SensorHealthSnapshot,
    TelemetryIngestPayload,
    TelemetryIngestResponse,
)
from app.schemas.readings import RainfallReadingRead, RiverReadingRead, SoilMoistureReadingRead
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/sensors", tags=["Sensors & Telemetry"])

def _get_sensor_latest_reading(db: Session, sensor: Sensor) -> Optional[Dict[str, Any]]:
    """
    Helper to fetch the latest recorded reading for a sensor.
    """
    if sensor.sensor_type in (SensorType.RAINFALL, SensorType.MULTI_SENSOR):
        rain = db.query(RainfallReading).filter(RainfallReading.sensor_id == sensor.id).order_by(desc(RainfallReading.timestamp)).first()
        if rain:
            return {
                "type": "RAINFALL",
                "value": rain.rainfall_mm,
                "unit": "mm/hr",
                "timestamp": rain.timestamp.isoformat()
            }
    
    if sensor.sensor_type == SensorType.RIVER_LEVEL:
        riv = db.query(RiverReading).filter(RiverReading.sensor_id == sensor.id).order_by(desc(RiverReading.timestamp)).first()
        if riv:
            return {
                "type": "RIVER_LEVEL",
                "value": riv.water_level_m,
                "flow_rate": riv.flow_rate,
                "unit": "m",
                "timestamp": riv.timestamp.isoformat()
            }
            
    if sensor.sensor_type == SensorType.SOIL_MOISTURE:
        soil = db.query(SoilMoistureReading).filter(SoilMoistureReading.sensor_id == sensor.id).order_by(desc(SoilMoistureReading.timestamp)).first()
        if soil:
            return {
                "type": "SOIL_MOISTURE",
                "value": soil.moisture_percentage,
                "unit": "%",
                "timestamp": soil.timestamp.isoformat()
            }

    if sensor.sensor_type == SensorType.WEATHER:
        # Weather multi-reading
        rain = db.query(RainfallReading).filter(RainfallReading.sensor_id == sensor.id).order_by(desc(RainfallReading.timestamp)).first()
        if rain:
            return {
                "type": "WEATHER",
                "value": rain.rainfall_mm,
                "unit": "mm/hr",
                "timestamp": rain.timestamp.isoformat()
            }

    return None

def _get_sensor_signal_strength(db: Session, sensor_id: int) -> float:
    health = db.query(SensorHealth).filter(SensorHealth.sensor_id == sensor_id).order_by(desc(SensorHealth.recorded_at)).first()
    return health.signal_strength if health else -72.0

@router.get("", response_model=List[SensorRead])
def list_sensors(
    sensor_type: Optional[SensorType] = Query(None, description="Filter by sensor type"),
    status: Optional[SensorStatus] = Query(None, description="Filter by status"),
    watershed_id: Optional[int] = Query(None, description="Filter by watershed ID"),
    search: Optional[str] = Query(None, description="Search by name, code or village"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all telemetry sensors with their latest readings, battery, signal strength and watershed name.
    Supports multi-criteria filtering.
    """
    query = db.query(Sensor)

    if sensor_type:
        query = query.filter(Sensor.sensor_type == sensor_type)
    if status:
        query = query.filter(Sensor.status == status)
    if watershed_id:
        query = query.filter(Sensor.watershed_id == watershed_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Sensor.name.ilike(search_pattern)) | 
            (Sensor.sensor_code.ilike(search_pattern)) |
            (Sensor.village.ilike(search_pattern))
        )

    sensors = query.offset(skip).limit(limit).all()

    # Enrich with latest reading and watershed name
    enriched: List[Dict[str, Any]] = []
    for s in sensors:
        ws_name = s.watershed.name if s.watershed else None
        latest = _get_sensor_latest_reading(db, s)
        signal = _get_sensor_signal_strength(db, s.id)
        
        enriched.append({
            "id": s.id,
            "sensor_code": s.sensor_code,
            "name": s.name,
            "sensor_type": s.sensor_type,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "elevation": s.elevation,
            "village": s.village,
            "watershed_id": s.watershed_id,
            "watershed_name": ws_name,
            "status": s.status,
            "battery_level": s.battery_level,
            "signal_strength": signal,
            "last_seen": s.last_seen,
            "created_at": s.created_at,
            "latest_reading": latest
        })

    return enriched

@router.get("/health", response_model=SensorHealthOverview)
def get_sensors_health_overview(db: Session = Depends(get_db)) -> Any:
    """
    Aggregate health diagnostics across all mountain telemetry edge nodes.
    """
    sensors = db.query(Sensor).all()
    total = len(sensors)
    
    active_cnt = sum(1 for s in sensors if s.status == SensorStatus.ACTIVE)
    offline_cnt = sum(1 for s in sensors if s.status == SensorStatus.OFFLINE)
    maint_cnt = sum(1 for s in sensors if s.status == SensorStatus.MAINTENANCE)
    inactive_cnt = sum(1 for s in sensors if s.status == SensorStatus.INACTIVE)
    
    avg_bat = round(sum(s.battery_level for s in sensors) / total, 1) if total > 0 else 0.0
    low_bat_cnt = sum(1 for s in sensors if s.battery_level < 25.0)

    snapshots: List[SensorHealthSnapshot] = []
    signals: List[float] = []

    for s in sensors:
        sig = _get_sensor_signal_strength(db, s.id)
        signals.append(sig)
        snapshots.append(SensorHealthSnapshot(
            id=s.id,
            sensor_code=s.sensor_code,
            name=s.name,
            sensor_type=s.sensor_type,
            status=s.status,
            battery_level=s.battery_level,
            signal_strength=sig,
            last_seen=s.last_seen,
            village=s.village,
            watershed_name=s.watershed.name if s.watershed else None
        ))

    avg_sig = round(sum(signals) / len(signals), 1) if signals else -70.0

    return SensorHealthOverview(
        total_sensors=total,
        active_count=active_cnt,
        offline_count=offline_cnt,
        maintenance_count=maint_cnt,
        inactive_count=inactive_cnt,
        avg_battery=avg_bat,
        low_battery_count=low_bat_cnt,
        avg_signal=avg_sig,
        sensors=snapshots
    )

@router.get("/{sensor_id}", response_model=SensorRead)
def get_sensor_by_id(sensor_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Retrieve sensor by primary key with latest telemetry payload.
    """
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor ID {sensor_id} not found")

    ws_name = sensor.watershed.name if sensor.watershed else None
    latest = _get_sensor_latest_reading(db, sensor)
    signal = _get_sensor_signal_strength(db, sensor.id)

    return {
        "id": sensor.id,
        "sensor_code": sensor.sensor_code,
        "name": sensor.name,
        "sensor_type": sensor.sensor_type,
        "latitude": sensor.latitude,
        "longitude": sensor.longitude,
        "elevation": sensor.elevation,
        "village": sensor.village,
        "watershed_id": sensor.watershed_id,
        "watershed_name": ws_name,
        "status": sensor.status,
        "battery_level": sensor.battery_level,
        "signal_strength": signal,
        "last_seen": sensor.last_seen,
        "created_at": sensor.created_at,
        "latest_reading": latest
    }

@router.get("/{sensor_id}/readings")
def get_sensor_readings(
    sensor_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve polymorphic historical readings for a sensor.
    Automatically returns rainfall, river level, or soil moisture based on the sensor's type.
    """
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor ID {sensor_id} not found")

    result: Dict[str, Any] = {
        "sensor_id": sensor.id,
        "sensor_code": sensor.sensor_code,
        "sensor_type": sensor.sensor_type,
        "name": sensor.name,
        "readings": []
    }

    if sensor.sensor_type in (SensorType.RAINFALL, SensorType.WEATHER):
        readings = db.query(RainfallReading).filter(RainfallReading.sensor_id == sensor.id).order_by(desc(RainfallReading.timestamp)).limit(limit).all()
        result["unit"] = "mm/hr"
        result["readings"] = [
            {"id": r.id, "value": r.rainfall_mm, "rainfall_mm": r.rainfall_mm, "timestamp": r.timestamp.isoformat()}
            for r in readings
        ]
    elif sensor.sensor_type == SensorType.RIVER_LEVEL:
        readings = db.query(RiverReading).filter(RiverReading.sensor_id == sensor.id).order_by(desc(RiverReading.timestamp)).limit(limit).all()
        result["unit"] = "m"
        result["readings"] = [
            {"id": r.id, "value": r.water_level_m, "water_level_m": r.water_level_m, "flow_rate": r.flow_rate, "timestamp": r.timestamp.isoformat()}
            for r in readings
        ]
    elif sensor.sensor_type == SensorType.SOIL_MOISTURE:
        readings = db.query(SoilMoistureReading).filter(SoilMoistureReading.sensor_id == sensor.id).order_by(desc(SoilMoistureReading.timestamp)).limit(limit).all()
        result["unit"] = "%"
        result["readings"] = [
            {"id": r.id, "value": r.moisture_percentage, "moisture_percentage": r.moisture_percentage, "timestamp": r.timestamp.isoformat()}
            for r in readings
        ]
    else:
        # Multi-sensor: return rainfall + river if present
        rain_readings = db.query(RainfallReading).filter(RainfallReading.sensor_id == sensor.id).order_by(desc(RainfallReading.timestamp)).limit(limit).all()
        result["unit"] = "multi"
        result["readings"] = [
            {"id": r.id, "value": r.rainfall_mm, "rainfall_mm": r.rainfall_mm, "timestamp": r.timestamp.isoformat()}
            for r in rain_readings
        ]

    return result

@router.get("/{sensor_id}/readings/rainfall", response_model=List[RainfallReadingRead])
def get_sensor_rainfall_readings(
    sensor_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get raw rainfall readings."""
    return db.query(RainfallReading).filter(RainfallReading.sensor_id == sensor_id).order_by(desc(RainfallReading.timestamp)).limit(limit).all()

@router.get("/{sensor_id}/readings/river", response_model=List[RiverReadingRead])
def get_sensor_river_readings(
    sensor_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get raw river readings."""
    return db.query(RiverReading).filter(RiverReading.sensor_id == sensor_id).order_by(desc(RiverReading.timestamp)).limit(limit).all()

@router.get("/{sensor_id}/readings/soil-moisture", response_model=List[SoilMoistureReadingRead])
def get_sensor_soil_moisture_readings(
    sensor_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get raw soil moisture readings."""
    return db.query(SoilMoistureReading).filter(SoilMoistureReading.sensor_id == sensor_id).order_by(desc(SoilMoistureReading.timestamp)).limit(limit).all()

@router.post("/ingest", response_model=TelemetryIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_sensor_reading(
    payload: TelemetryIngestPayload,
    db: Session = Depends(get_db)
) -> Any:
    """
    Ingest a new real-time sensor reading or health status.
    Stores record in the database and broadcasts live through WebSockets.
    """
    sensor = None
    if payload.sensor_id:
        sensor = db.query(Sensor).filter(Sensor.id == payload.sensor_id).first()
    elif payload.sensor_code:
        sensor = db.query(Sensor).filter(Sensor.sensor_code == payload.sensor_code).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found for given id or code")

    now = payload.timestamp or datetime.now(timezone.utc)
    readings_created: List[str] = []

    # 1. Update Sensor state
    sensor.last_seen = now
    if payload.battery_level is not None:
        sensor.battery_level = payload.battery_level
    if payload.status is not None:
        sensor.status = payload.status

    # 2. Add Readings
    if payload.rainfall_mm is not None:
        rain = RainfallReading(
            sensor_id=sensor.id,
            rainfall_mm=payload.rainfall_mm,
            timestamp=now
        )
        db.add(rain)
        readings_created.append("rainfall")

    if payload.water_level_m is not None:
        river = RiverReading(
            sensor_id=sensor.id,
            water_level_m=payload.water_level_m,
            flow_rate=payload.flow_rate,
            timestamp=now
        )
        db.add(river)
        readings_created.append("river_level")

    if payload.moisture_percentage is not None:
        soil = SoilMoistureReading(
            sensor_id=sensor.id,
            moisture_percentage=payload.moisture_percentage,
            timestamp=now
        )
        db.add(soil)
        readings_created.append("soil_moisture")

    # 3. Add Sensor Health Log
    signal = payload.signal_strength if payload.signal_strength is not None else -68.0
    health_log = SensorHealth(
        sensor_id=sensor.id,
        battery_level=sensor.battery_level,
        signal_strength=signal,
        status=sensor.status,
        last_seen=now,
        recorded_at=now
    )
    db.add(health_log)

    db.commit()
    db.refresh(sensor)

    # 4. Broadcast via WebSocket
    broadcast_data = {
        "event": "sensor_reading",
        "data": {
            "sensor_id": sensor.id,
            "sensor_code": sensor.sensor_code,
            "name": sensor.name,
            "sensor_type": sensor.sensor_type.value,
            "status": sensor.status.value,
            "battery_level": sensor.battery_level,
            "signal_strength": signal,
            "rainfall_mm": payload.rainfall_mm,
            "water_level_m": payload.water_level_m,
            "flow_rate": payload.flow_rate,
            "moisture_percentage": payload.moisture_percentage,
            "last_seen": now.isoformat(),
            "watershed_id": sensor.watershed_id,
            "watershed_name": sensor.watershed.name if sensor.watershed else None
        }
    }

    try:
        await ws_manager.broadcast_json(broadcast_data)
        broadcasted = True
    except Exception:
        broadcasted = False

    return TelemetryIngestResponse(
        status="ingested",
        sensor_id=sensor.id,
        sensor_code=sensor.sensor_code,
        readings_created=readings_created,
        broadcasted=broadcasted,
        timestamp=now
    )

