"""
Citizen Report Sensor-Correlation Verification Engine.

Cross-references geo-tagged citizen ground reports against physical telemetry
from nearby rainfall gauges, river stage radars, and soil moisture probes to calculate
an objective corroboration confidence score.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.citizen_report import CitizenReport
from app.models.sensor import Sensor
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.enums import CitizenReportType, SensorType


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes approximate Haversine distance between two coordinates in kilometers.
    """
    earth_radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2 +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(earth_radius * c, 2)


class CitizenVerificationEngine:
    """
    Evaluates sensor proximity and physical reading correlation to support
    response teams during ground truth report verification.
    """

    def correlate_report_with_sensors(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        report_type: CitizenReportType,
        has_image: bool = False,
        max_radius_km: float = 20.0
    ) -> Dict[str, Any]:
        """
        Cross-references report coordinates with telemetry from all sensors within max_radius_km.
        """
        sensors = db.query(Sensor).all()
        nearby_sensor_items: List[Dict[str, Any]] = []
        matching_reasons: List[str] = []

        base_confidence = 35.0
        confidence_delta = 0.0

        if has_image:
            confidence_delta += 15.0
            matching_reasons.append("Photo evidence provided by citizen.")

        # Find nearby sensors and inspect latest readings
        for s in sensors:
            dist = calculate_distance_km(latitude, longitude, s.latitude, s.longitude)
            if dist <= max_radius_km:
                latest_reading_dict: Optional[Dict[str, Any]] = None
                is_corroborating = False
                corroboration_note = ""

                # 1. Rainfall sensors
                if s.sensor_type in (SensorType.RAINFALL, SensorType.MULTI_SENSOR):
                    rain = db.query(RainfallReading).filter(
                        RainfallReading.sensor_id == s.id
                    ).order_by(desc(RainfallReading.timestamp)).first()
                    if rain:
                        latest_reading_dict = {
                            "type": "RAINFALL",
                            "value": rain.rainfall_mm,
                            "unit": "mm/hr",
                            "timestamp": rain.timestamp.isoformat()
                        }
                        if report_type in (CitizenReportType.HEAVY_RAINFALL, CitizenReportType.FLASH_FLOOD, CitizenReportType.RIVER_RISING):
                            if rain.rainfall_mm >= 30.0:
                                is_corroborating = True
                                corroboration_note = f"High rainfall ({rain.rainfall_mm:.1f} mm/hr) detected at {dist:.1f} km."
                                confidence_delta += 25.0 * max(0.4, (1.0 - (dist / max_radius_km)))
                            elif rain.rainfall_mm >= 12.0:
                                is_corroborating = True
                                corroboration_note = f"Moderate rainfall ({rain.rainfall_mm:.1f} mm/hr) at {dist:.1f} km."
                                confidence_delta += 12.0 * max(0.4, (1.0 - (dist / max_radius_km)))

                # 2. River water level sensors
                if s.sensor_type in (SensorType.RIVER_LEVEL, SensorType.MULTI_SENSOR):
                    riv = db.query(RiverReading).filter(
                        RiverReading.sensor_id == s.id
                    ).order_by(desc(RiverReading.timestamp)).first()
                    if riv:
                        latest_reading_dict = {
                            "type": "RIVER_LEVEL",
                            "value": riv.water_level_m,
                            "unit": "m",
                            "flow_rate": riv.flow_rate,
                            "timestamp": riv.timestamp.isoformat()
                        }
                        if report_type in (
                            CitizenReportType.RIVER_RISING,
                            CitizenReportType.WATER_OVERFLOW,
                            CitizenReportType.FLASH_FLOOD,
                            CitizenReportType.ROAD_BLOCKAGE,
                            CitizenReportType.ROAD_BLOCKED,
                            CitizenReportType.BRIDGE_DAMAGE,
                            CitizenReportType.STRUCTURAL_DAMAGE
                        ):
                            if riv.water_level_m >= 4.0:
                                is_corroborating = True
                                corroboration_note = f"Critical stage ({riv.water_level_m:.2f}m) detected at {dist:.1f} km."
                                confidence_delta += 30.0 * max(0.4, (1.0 - (dist / max_radius_km)))
                            elif riv.water_level_m >= 3.0:
                                is_corroborating = True
                                corroboration_note = f"Elevated stage ({riv.water_level_m:.2f}m) detected at {dist:.1f} km."
                                confidence_delta += 18.0 * max(0.4, (1.0 - (dist / max_radius_km)))

                # 3. Soil moisture sensors
                if s.sensor_type in (SensorType.SOIL_MOISTURE, SensorType.MULTI_SENSOR):
                    soil = db.query(SoilMoistureReading).filter(
                        SoilMoistureReading.sensor_id == s.id
                    ).order_by(desc(SoilMoistureReading.timestamp)).first()
                    if soil:
                        latest_reading_dict = {
                            "type": "SOIL_MOISTURE",
                            "value": soil.moisture_percentage,
                            "unit": "%",
                            "timestamp": soil.timestamp.isoformat()
                        }
                        if report_type in (CitizenReportType.LANDSLIDE, CitizenReportType.ROAD_BLOCKAGE, CitizenReportType.ROAD_BLOCKED):
                            if soil.moisture_percentage >= 80.0:
                                is_corroborating = True
                                corroboration_note = f"High soil saturation ({soil.moisture_percentage:.1f}%) detected at {dist:.1f} km."
                                confidence_delta += 28.0 * max(0.4, (1.0 - (dist / max_radius_km)))

                if is_corroborating and corroboration_note:
                    matching_reasons.append(corroboration_note)

                sensor_item = {
                    "sensor_id": s.id,
                    "sensor_name": s.name,
                    "sensor_type": s.sensor_type.value if hasattr(s.sensor_type, "value") else str(s.sensor_type),
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "distance_km": dist,
                    "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                    "latest_reading": latest_reading_dict,
                    "is_corroborating": is_corroborating,
                    "corroboration_note": corroboration_note
                }
                nearby_sensor_items.append(sensor_item)

        # Sort nearby sensors by proximity
        nearby_sensor_items.sort(key=lambda x: x["distance_km"])

        # Final calculated confidence
        final_confidence = min(98.0, max(15.0, base_confidence + confidence_delta))

        if not matching_reasons:
            matching_reasons.append("No immediate sensor anomalies detected in vicinity.")

        return {
            "confidence_score": round(final_confidence, 1),
            "nearby_sensors_count": len(nearby_sensor_items),
            "corroborating_sensors_count": sum(1 for s in nearby_sensor_items if s["is_corroborating"]),
            "nearby_sensors": nearby_sensor_items[:8],
            "matching_reasons": matching_reasons
        }


# Singleton instance
citizen_verification_engine = CitizenVerificationEngine()
