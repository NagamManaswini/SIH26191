"""
Real-Time Alert Engine for Flash Flood Early Warning System.

Evaluates multi-factor hydrological telemetry, explainable risk scores,
and temporal AI multi-horizon forecasts to trigger intelligent, deduplicated
flash flood emergency alerts.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.models.alert import Alert
from app.models.watershed import Watershed
from app.models.sensor import Sensor
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.prediction import FloodPrediction
from app.models.enums import AlertType, AlertSeverity, AlertStatus, SensorType, RiskLevel
from app.services.notification_service import notification_service
from app.websocket.manager import ws_manager

logger = logging.getLogger("alert_engine")

# Severity Hierarchy for escalation comparisons
SEVERITY_WEIGHT = {
    AlertSeverity.INFO: 1,
    AlertSeverity.ADVISORY: 1,
    AlertSeverity.WATCH: 2,
    AlertSeverity.WARNING: 3,
    AlertSeverity.DANGER: 4,
    AlertSeverity.EMERGENCY: 5,
}


def calculate_danger_zone_polygon(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    num_points: int = 24
) -> List[List[float]]:
    """
    Generates a GeoJSON polygon ring (list of [longitude, latitude] coordinates)
    approximating a circular geo-fenced danger buffer around a point.
    """
    coordinates: List[List[float]] = []
    # Earth radius in kilometers
    earth_radius = 6371.0
    
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)
    
    for i in range(num_points):
        bearing = (2 * math.pi * i) / num_points
        
        # Spherical trigonometry destination point
        point_lat = math.asin(
            math.sin(lat_rad) * math.cos(radius_km / earth_radius) +
            math.cos(lat_rad) * math.sin(radius_km / earth_radius) * math.cos(bearing)
        )
        point_lon = lon_rad + math.atan2(
            math.sin(bearing) * math.sin(radius_km / earth_radius) * math.cos(lat_rad),
            math.cos(radius_km / earth_radius) - math.sin(lat_rad) * math.sin(point_lat)
        )
        
        coordinates.append([
            round(math.degrees(point_lon), 5),
            round(math.degrees(point_lat), 5)
        ])
        
    # Close polygon ring by repeating first vertex
    coordinates.append(coordinates[0])
    return coordinates


def get_watershed_centroid(watershed: Watershed, db: Session) -> Tuple[float, float]:
    """
    Computes latitude, longitude centroid for a watershed from its sensors or geometry.
    """
    sensors = db.query(Sensor).filter(Sensor.watershed_id == watershed.id).all()
    if sensors:
        avg_lat = sum(s.latitude for s in sensors) / len(sensors)
        avg_lon = sum(s.longitude for s in sensors) / len(sensors)
        return round(avg_lat, 5), round(avg_lon, 5)
    return 30.65, 79.15


class AlertEngine:
    """
    Core Alert Engine implementing rule-based severity evaluation,
    intelligent duplicate prevention, and multi-channel emergency dispatching.
    """

    def evaluate_rules(
        self,
        current_risk_level: str,
        river_stage_m: float,
        river_rate_of_rise: float,
        rainfall_intensity_mm_hr: float,
        accumulated_rain_mm: float,
        soil_saturation_pct: float,
        predicted_max_stage_m: float,
        predicted_max_risk: str,
        predicted_flood_prob_pct: float,
        lead_time_min: int = 60
    ) -> Optional[Tuple[AlertSeverity, AlertType, str, str, List[str]]]:
        """
        Evaluates rule matrix across hydrological features.
        Returns: (severity, alert_type, title, message, reasons) or None if safe.
        """
        reasons: List[str] = []
        severity: Optional[AlertSeverity] = None
        alert_type: AlertType = AlertType.FLASH_FLOOD

        # 1. EMERGENCY Conditions
        if (
            current_risk_level == "CRITICAL"
            or river_stage_m >= 4.5
            or predicted_flood_prob_pct >= 85.0
            or (predicted_max_risk == "CRITICAL" and lead_time_min <= 60)
            or (river_rate_of_rise >= 1.0 and rainfall_intensity_mm_hr >= 60.0)
        ):
            severity = AlertSeverity.EMERGENCY
            alert_type = AlertType.EVACUATION_WARNING
            if current_risk_level == "CRITICAL":
                reasons.append(f"Current catchment risk evaluated as CRITICAL.")
            if river_stage_m >= 4.5:
                reasons.append(f"River stage ({river_stage_m:.2f}m) has breached critical danger threshold (4.50m).")
            if predicted_flood_prob_pct >= 85.0:
                reasons.append(f"AI inundation forecast probability is {predicted_flood_prob_pct:.1f}% within next 2 hours.")
            if river_rate_of_rise >= 1.0:
                reasons.append(f"Rapid cloudburst flood surge detected: rate of rise is {river_rate_of_rise:.2f} m/hr.")
            if soil_saturation_pct >= 85.0:
                reasons.append(f"Soil is fully saturated ({soil_saturation_pct:.1f}%), accelerating runoff.")

            title = "EMERGENCY: Imminent Flash Flood & Dam Breach Warning"
            message = (
                f"Severe flash flood surge active. River stage at {river_stage_m:.2f}m with {predicted_flood_prob_pct:.0f}% inundation probability. "
                f"Mandatory evacuation advised for low-lying floodplain communities."
            )
            return severity, alert_type, title, message, reasons

        # 2. DANGER Conditions
        if (
            current_risk_level == "HIGH"
            or river_stage_m >= 3.8
            or predicted_max_risk == "HIGH"
            or predicted_flood_prob_pct >= 60.0
            or river_rate_of_rise >= 0.50
            or (rainfall_intensity_mm_hr >= 45.0 and soil_saturation_pct >= 75.0)
        ):
            severity = AlertSeverity.DANGER
            alert_type = AlertType.FLASH_FLOOD
            if current_risk_level == "HIGH":
                reasons.append(f"Catchment risk level is HIGH.")
            if river_stage_m >= 3.8:
                reasons.append(f"River stage ({river_stage_m:.2f}m) approaching danger mark (4.50m).")
            if predicted_flood_prob_pct >= 60.0:
                reasons.append(f"AI forecast indicates {predicted_flood_prob_pct:.1f}% flood probability at +{lead_time_min}m.")
            if river_rate_of_rise >= 0.50:
                reasons.append(f"Fast water elevation detected: {river_rate_of_rise:.2f} m/hr rate of rise.")
            if rainfall_intensity_mm_hr >= 45.0:
                reasons.append(f"Heavy precipitation: {rainfall_intensity_mm_hr:.1f} mm/hr intensity.")

            title = "DANGER: High Flash Flood Risk Detected"
            message = (
                f"High water level surge imminent. Water stage at {river_stage_m:.2f}m rising at {river_rate_of_rise:.2f}m/hr. "
                f"Response teams activated. Avoid riverbanks and vulnerable road crossings."
            )
            return severity, alert_type, title, message, reasons

        # 3. WARNING Conditions
        if (
            current_risk_level == "MODERATE"
            or river_stage_m >= 3.2
            or rainfall_intensity_mm_hr >= 30.0
            or accumulated_rain_mm >= 50.0
            or river_rate_of_rise >= 0.30
            or soil_saturation_pct >= 80.0
        ):
            severity = AlertSeverity.WARNING
            alert_type = AlertType.RIVER_RISE if river_stage_m >= 3.2 else AlertType.CLOUDBURST
            if rainfall_intensity_mm_hr >= 30.0:
                reasons.append(f"Moderate to heavy rainfall recorded: {rainfall_intensity_mm_hr:.1f} mm/hr.")
            if river_stage_m >= 3.2:
                reasons.append(f"River stage ({river_stage_m:.2f}m) exceeds warning mark (3.20m).")
            if river_rate_of_rise >= 0.30:
                reasons.append(f"River rate of rise elevated at {river_rate_of_rise:.2f} m/hr.")
            if soil_saturation_pct >= 80.0:
                reasons.append(f"Soil moisture elevated at {soil_saturation_pct:.1f}%.")

            title = "WARNING: Flood Advisory & Rising Water Stage"
            message = (
                f"Elevated runoff and rising water levels observed in catchment. River stage at {river_stage_m:.2f}m. "
                f"Stay vigilant and monitor emergency channels."
            )
            return severity, alert_type, title, message, reasons

        # 4. INFO Conditions (Precautionary)
        if rainfall_intensity_mm_hr >= 15.0 or river_stage_m >= 2.5:
            severity = AlertSeverity.INFO
            alert_type = AlertType.FLASH_FLOOD
            reasons.append(f"Moderate rainfall ({rainfall_intensity_mm_hr:.1f} mm/hr) in upper catchment.")
            title = "INFO: Hydrological Monitoring Notice"
            message = f"Catchment sensors active. Normal to elevated flow ({river_stage_m:.2f}m). No immediate threat."
            return severity, alert_type, title, message, reasons

        return None

    def find_active_alert_for_watershed(
        self,
        db: Session,
        watershed_lat: float,
        watershed_lon: float,
        cooldown_minutes: int = 45
    ) -> Optional[Alert]:
        """
        Finds active or unexpired alert within proximity of the watershed.
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)
        
        # Look for active alerts near the coordinates
        alerts = db.query(Alert).filter(
            Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]),
            Alert.created_at >= cutoff_time
        ).all()
        
        for a in alerts:
            dist = math.sqrt((a.latitude - watershed_lat)**2 + (a.longitude - watershed_lon)**2) * 111.0
            if dist <= max(a.radius_km, 8.0):
                return a
                
        return None

    def evaluate_watershed(self, db: Session, watershed: Watershed) -> Dict[str, Any]:
        """
        Evaluates real-time sensor data, risk status, and predictions for a single watershed.
        Creates or escalates alert if needed.
        """
        # 1. Fetch latest telemetry for watershed
        sensors = db.query(Sensor).filter(Sensor.watershed_id == watershed.id).all()
        sensor_ids = [s.id for s in sensors]
        
        rainfall_intensity = 0.0
        accumulated_rain = 0.0
        river_stage = 2.0
        rate_of_rise = 0.0
        soil_saturation = 60.0

        if sensor_ids:
            # Rainfall
            rain_readings = db.query(RainfallReading).filter(
                RainfallReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(RainfallReading.timestamp)).limit(5).all()
            if rain_readings:
                rainfall_intensity = max(r.rainfall_mm for r in rain_readings)
                accumulated_rain = sum(r.rainfall_mm for r in rain_readings)

            # River
            river_readings = db.query(RiverReading).filter(
                RiverReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(RiverReading.timestamp)).limit(2).all()
            if river_readings:
                river_stage = river_readings[0].water_level_m
                if len(river_readings) > 1:
                    dt_hours = max(0.05, (river_readings[0].timestamp - river_readings[1].timestamp).total_seconds() / 3600.0)
                    rate_of_rise = max(0.0, (river_readings[0].water_level_m - river_readings[1].water_level_m) / dt_hours)

            # Soil
            soil_reading = db.query(SoilMoistureReading).filter(
                SoilMoistureReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(SoilMoistureReading.timestamp)).first()
            if soil_reading:
                soil_saturation = soil_reading.moisture_percentage

        # 2. Fetch latest AI predictions
        latest_preds = db.query(FloodPrediction).filter(
            FloodPrediction.watershed_id == watershed.id
        ).order_by(desc(FloodPrediction.prediction_time)).limit(4).all()

        predicted_max_stage = river_stage
        predicted_max_risk = "LOW"
        predicted_flood_prob = 15.0

        if latest_preds:
            predicted_max_stage = max(p.predicted_water_level for p in latest_preds)
            predicted_flood_prob = max(p.probability for p in latest_preds)
            if predicted_flood_prob > 75 or predicted_max_stage >= 4.5:
                predicted_max_risk = "CRITICAL"
            elif predicted_flood_prob > 45 or predicted_max_stage >= 3.5:
                predicted_max_risk = "HIGH"
            elif predicted_flood_prob > 20:
                predicted_max_risk = "MODERATE"

        current_risk_str = watershed.risk_level.value if hasattr(watershed.risk_level, "value") else str(watershed.risk_level)

        # 3. Evaluate rules
        eval_result = self.evaluate_rules(
            current_risk_level=current_risk_str,
            river_stage_m=river_stage,
            river_rate_of_rise=rate_of_rise,
            rainfall_intensity_mm_hr=rainfall_intensity,
            accumulated_rain_mm=accumulated_rain,
            soil_saturation_pct=soil_saturation,
            predicted_max_stage_m=predicted_max_stage,
            predicted_max_risk=predicted_max_risk,
            predicted_flood_prob_pct=predicted_flood_prob
        )

        if not eval_result:
            return {
                "watershed_id": watershed.id,
                "watershed_name": watershed.name,
                "action": "NO_ALERT_REQUIRED",
                "risk_level": current_risk_str,
                "stage": river_stage
            }

        severity, alert_type, title, message, reasons = eval_result
        ws_lat, ws_lon = get_watershed_centroid(watershed, db)

        # 4. Check for duplicate / escalation
        existing_alert = self.find_active_alert_for_watershed(
            db=db,
            watershed_lat=ws_lat,
            watershed_lon=ws_lon
        )

        if existing_alert:
            curr_weight = SEVERITY_WEIGHT.get(existing_alert.severity, 2)
            new_weight = SEVERITY_WEIGHT.get(severity, 2)
            
            if new_weight <= curr_weight:
                # Suppress duplicate alert
                logger.info(f"Duplicate alert suppressed for {watershed.name}. Active alert ID={existing_alert.id} ({existing_alert.severity}).")
                return {
                    "watershed_id": watershed.id,
                    "watershed_name": watershed.name,
                    "action": "DUPLICATE_SUPPRESSED",
                    "existing_alert_id": existing_alert.id,
                    "severity": existing_alert.severity.value if hasattr(existing_alert.severity, "value") else str(existing_alert.severity),
                    "reasons": reasons
                }
            else:
                # Escalate existing alert
                existing_alert.severity = severity
                existing_alert.title = f"[ESCALATED] {title}"
                existing_alert.message = message
                existing_alert.expires_at = datetime.now(timezone.utc) + timedelta(hours=3)
                db.commit()
                db.refresh(existing_alert)

                # Dispatch notifications
                receipts = notification_service.dispatch_alert(
                    alert_id=existing_alert.id,
                    title=existing_alert.title,
                    message=existing_alert.message,
                    severity=severity.value if hasattr(severity, "value") else str(severity),
                    affected_area=f"{watershed.name}, {watershed.district}",
                    metadata={"watershed_id": watershed.id, "reasons": reasons}
                )

                return {
                    "watershed_id": watershed.id,
                    "watershed_name": watershed.name,
                    "action": "ALERT_ESCALATED",
                    "alert_id": existing_alert.id,
                    "severity": severity.value if hasattr(severity, "value") else str(severity),
                    "reasons": reasons,
                    "dispatches": len(receipts)
                }

        # 5. Create new alert
        new_alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=f"{watershed.name}: {title}",
            message=message,
            latitude=ws_lat,
            longitude=ws_lon,
            radius_km=max(4.0, math.sqrt(watershed.area_sq_km) / 2.0 if watershed.area_sq_km else 5.0),
            status=AlertStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=3)
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        # Dispatch notifications across SMS, Voice, Push, Siren
        severity_str = severity.value if hasattr(severity, "value") else str(severity)
        receipts = notification_service.dispatch_alert(
            alert_id=new_alert.id,
            title=new_alert.title,
            message=new_alert.message,
            severity=severity_str,
            affected_area=f"{watershed.name} ({watershed.district})",
            metadata={"watershed_id": watershed.id, "reasons": reasons}
        )

        return {
            "watershed_id": watershed.id,
            "watershed_name": watershed.name,
            "action": "ALERT_CREATED",
            "alert_id": new_alert.id,
            "severity": severity_str,
            "reasons": reasons,
            "dispatches": len(receipts)
        }

    def evaluate_all_watersheds(self, db: Session) -> List[Dict[str, Any]]:
        """
        Evaluates alert conditions across all watersheds in the platform.
        """
        watersheds = db.query(Watershed).all()
        results: List[Dict[str, Any]] = []
        for ws in watersheds:
            res = self.evaluate_watershed(db, ws)
            results.append(res)
        return results

    def acknowledge_alert(self, db: Session, alert_id: int) -> Optional[Alert]:
        """
        Acknowledges an active alert and records acknowledgment.
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
            
        alert.status = AlertStatus.ACKNOWLEDGED
        db.commit()
        db.refresh(alert)
        return alert


# Singleton instance
alert_engine = AlertEngine()
