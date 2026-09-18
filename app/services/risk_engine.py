from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.watershed import Watershed
from app.models.sensor import Sensor
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.historical import HistoricalFloodEvent
from app.models.risk_config import RiskConfiguration
from app.models.enums import RiskLevel, SensorType


class ExplainableFloodRiskEngine:
    """
    Transparent, physics-grounded, explainable weighted flood risk assessment engine.
    Calculates multi-factor hydrological, morphological, and historical risk scores (0-100).
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def get_active_configuration(self, db: Session) -> RiskConfiguration:
        """Fetch active risk weighting configuration or instantiate default."""
        config = db.query(RiskConfiguration).filter(RiskConfiguration.is_active == True).first()
        if not config:
            config = RiskConfiguration(
                config_name="Standard Himalayan Monsoon V1",
                is_active=True,
                weight_rainfall=0.25,
                weight_accumulated_rain=0.15,
                weight_river_level=0.20,
                weight_rate_of_rise=0.15,
                weight_soil_moisture=0.10,
                weight_slope=0.08,
                weight_historical=0.07,
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config

    def score_rainfall_intensity(self, intensity_mm_hr: float, threshold_mod: float = 15.0, threshold_crit: float = 40.0) -> float:
        """Calculate 0-100 score for instantaneous rainfall intensity."""
        if intensity_mm_hr <= 2.0:
            return max(5.0, intensity_mm_hr * 4.0)
        elif intensity_mm_hr <= threshold_mod:
            return 10.0 + 35.0 * ((intensity_mm_hr - 2.0) / (threshold_mod - 2.0))
        elif intensity_mm_hr <= threshold_crit:
            return 45.0 + 40.0 * ((intensity_mm_hr - threshold_mod) / (threshold_crit - threshold_mod))
        else:
            return min(100.0, 85.0 + 15.0 * ((intensity_mm_hr - threshold_crit) / 30.0))

    def score_accumulated_rainfall(self, accumulated_3h_mm: float, threshold_crit: float = 60.0) -> float:
        """Calculate 0-100 score for 3-hour cumulative rainfall."""
        if accumulated_3h_mm <= 10.0:
            return max(5.0, accumulated_3h_mm * 1.5)
        elif accumulated_3h_mm <= 35.0:
            return 15.0 + 35.0 * ((accumulated_3h_mm - 10.0) / 25.0)
        elif accumulated_3h_mm <= threshold_crit:
            return 50.0 + 35.0 * ((accumulated_3h_mm - 35.0) / (threshold_crit - 35.0))
        else:
            return min(100.0, 85.0 + 15.0 * ((accumulated_3h_mm - threshold_crit) / 40.0))

    def score_river_stage(self, water_level_m: float, danger_threshold_m: float = 3.5, critical_threshold_m: float = 4.8) -> float:
        """Calculate 0-100 score for river gauge water depth."""
        if water_level_m <= 1.5:
            return 10.0
        elif water_level_m <= danger_threshold_m:
            return 10.0 + 45.0 * ((water_level_m - 1.5) / (danger_threshold_m - 1.5))
        elif water_level_m <= critical_threshold_m:
            return 55.0 + 35.0 * ((water_level_m - danger_threshold_m) / (critical_threshold_m - danger_threshold_m))
        else:
            return min(100.0, 90.0 + 10.0 * ((water_level_m - critical_threshold_m) / 2.0))

    def score_rate_of_rise(self, rate_of_rise_m_hr: float, threshold_crit: float = 0.40) -> float:
        """Calculate 0-100 score for river hydrograph slope (rate of rise)."""
        if rate_of_rise_m_hr <= 0.0:
            return 5.0
        elif rate_of_rise_m_hr <= 0.20:
            return 5.0 + 35.0 * (rate_of_rise_m_hr / 0.20)
        elif rate_of_rise_m_hr <= threshold_crit:
            return 40.0 + 45.0 * ((rate_of_rise_m_hr - 0.20) / (threshold_crit - 0.20))
        else:
            return min(100.0, 85.0 + 15.0 * ((rate_of_rise_m_hr - threshold_crit) / 0.40))

    def score_soil_moisture(self, moisture_pct: float, threshold_crit: float = 80.0) -> float:
        """Calculate 0-100 score for catchment soil saturation percentage."""
        if moisture_pct <= 40.0:
            return 10.0
        elif moisture_pct <= 65.0:
            return 10.0 + 35.0 * ((moisture_pct - 40.0) / 25.0)
        elif moisture_pct <= threshold_crit:
            return 45.0 + 40.0 * ((moisture_pct - 65.0) / (threshold_crit - 65.0))
        else:
            return min(100.0, 85.0 + 15.0 * ((moisture_pct - threshold_crit) / 20.0))

    def score_slope(self, slope_deg: float, threshold_steep: float = 25.0) -> float:
        """Calculate 0-100 score for topographical steepness and runoff acceleration."""
        if slope_deg <= 10.0:
            return 20.0
        elif slope_deg <= threshold_steep:
            return 20.0 + 45.0 * ((slope_deg - 10.0) / (threshold_steep - 10.0))
        elif slope_deg <= 40.0:
            return 65.0 + 25.0 * ((slope_deg - threshold_steep) / 15.0)
        else:
            return 95.0

    def score_historical_risk(self, events_count: int, worst_event_severity: str = "MODERATE") -> float:
        """Calculate 0-100 score for historical catchment vulnerability."""
        if events_count == 0:
            return 15.0
        elif events_count == 1:
            return 45.0 if worst_event_severity != "CRITICAL" else 65.0
        elif events_count <= 3:
            return 75.0 if worst_event_severity != "CRITICAL" else 88.0
        else:
            return 95.0

    def categorize_risk(self, score: float) -> str:
        """Map 0-100 score to standardized risk category."""
        if score <= 25.0:
            return "LOW"
        elif score <= 50.0:
            return "MODERATE"
        elif score <= 75.0:
            return "HIGH"
        else:
            return "CRITICAL"

    def evaluate_watershed_risk(self, watershed_id: int, db: Session) -> Dict[str, Any]:
        """
        Evaluate full multi-factor explainable flood risk for a specific watershed.
        """
        watershed = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not watershed:
            raise ValueError(f"Watershed with ID {watershed_id} not found.")

        config = self.get_active_configuration(db)

        # 1. Fetch sensor telemetry in watershed
        sensor_ids = [s.id for s in watershed.sensors] if watershed.sensors else []
        now = datetime.now(timezone.utc)

        # Rainfall Intensity & 3h Cumulative
        current_rainfall = 0.0
        accumulated_rain_3h = 0.0
        if sensor_ids:
            rain_records = db.query(RainfallReading).filter(
                RainfallReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(RainfallReading.timestamp)).limit(15).all()
            if rain_records:
                current_rainfall = max(r.rainfall_mm for r in rain_records[:3])
                accumulated_rain_3h = round(sum(r.rainfall_mm for r in rain_records) * 0.75, 1)

        # River Water Level & Rate of Rise
        current_river_level = 1.85
        rate_of_rise = 0.0
        if sensor_ids:
            river_records = db.query(RiverReading).filter(
                RiverReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(RiverReading.timestamp)).limit(6).all()
            if river_records:
                current_river_level = river_records[0].water_level_m
                if len(river_records) >= 2:
                    dt_hours = max(0.1, (river_records[0].timestamp - river_records[-1].timestamp).total_seconds() / 3600.0) if river_records[0].timestamp and river_records[-1].timestamp else 0.5
                    dh = river_records[0].water_level_m - river_records[-1].water_level_m
                    rate_of_rise = round(max(0.0, dh / dt_hours), 2)

        # Soil Moisture
        current_soil_moisture = 62.0
        if sensor_ids:
            soil_records = db.query(SoilMoistureReading).filter(
                SoilMoistureReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(SoilMoistureReading.timestamp)).limit(5).all()
            if soil_records:
                current_soil_moisture = soil_records[0].moisture_percentage

        # Topographical Morphometry
        slope_deg = getattr(watershed, "average_slope_deg", 24.5)
        elevation_m = getattr(watershed, "elevation_m", 1850.0)

        # Historical Events
        historical_events = db.query(HistoricalFloodEvent).filter(
            HistoricalFloodEvent.location.ilike(f"%{watershed.name.split()[0]}%") |
            HistoricalFloodEvent.affected_area.ilike(f"%{watershed.district}%")
        ).all()
        events_count = len(historical_events)
        worst_event = historical_events[0] if historical_events else None
        worst_event_severity = worst_event.severity.value if worst_event and hasattr(worst_event.severity, "value") else "MODERATE"

        # 2. Calculate Individual Normalized Scores
        rain_score = self.score_rainfall_intensity(current_rainfall, config.threshold_rainfall_moderate_mm, config.threshold_rainfall_critical_mm)
        acc_rain_score = self.score_accumulated_rainfall(accumulated_rain_3h, config.threshold_accumulated_rain_3h_mm)
        river_score = self.score_river_stage(current_river_level, config.threshold_river_danger_m, config.threshold_river_critical_m)
        rise_score = self.score_rate_of_rise(rate_of_rise, config.threshold_rate_of_rise_m_hr)
        soil_score = self.score_soil_moisture(current_soil_moisture, config.threshold_soil_critical_pct)
        slope_score = self.score_slope(slope_deg, config.threshold_slope_steep_deg)
        hist_score = self.score_historical_risk(events_count, worst_event_severity)

        # 3. Calculate Weighted Composite Score
        total_weight = (
            config.weight_rainfall +
            config.weight_accumulated_rain +
            config.weight_river_level +
            config.weight_rate_of_rise +
            config.weight_soil_moisture +
            config.weight_slope +
            config.weight_historical
        )

        weighted_sum = (
            (rain_score * config.weight_rainfall) +
            (acc_rain_score * config.weight_accumulated_rain) +
            (river_score * config.weight_river_level) +
            (rise_score * config.weight_rate_of_rise) +
            (soil_score * config.weight_soil_moisture) +
            (slope_score * config.weight_slope) +
            (hist_score * config.weight_historical)
        )

        final_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0
        final_score = max(0.0, min(100.0, final_score))
        risk_level = self.categorize_risk(final_score)

        # 4. Generate Explainable Diagnostic Explanations
        explanations: List[str] = []
        if current_rainfall >= config.threshold_rainfall_critical_mm:
            explanations.append(f"Extreme convective rainfall intensity ({current_rainfall} mm/hr) exceeds critical threshold ({config.threshold_rainfall_critical_mm} mm/hr).")
        elif current_rainfall >= config.threshold_rainfall_moderate_mm:
            explanations.append(f"High rainfall rate of {current_rainfall} mm/hr detected across catchment gauges.")

        if accumulated_rain_3h >= config.threshold_accumulated_rain_3h_mm:
            explanations.append(f"Heavy 3-hour storm accumulation ({accumulated_rain_3h} mm) priming rapid surface runoff.")

        if current_river_level >= config.threshold_river_critical_m:
            explanations.append(f"River gauge stage ({current_river_level} m) has breached critical danger flood level ({config.threshold_river_critical_m} m).")
        elif current_river_level >= config.threshold_river_danger_m:
            explanations.append(f"River water stage ({current_river_level} m) is approaching bankfull warning threshold ({config.threshold_river_danger_m} m).")

        if rate_of_rise >= config.threshold_rate_of_rise_m_hr:
            explanations.append(f"Rapid hydrograph rate of rise (+{rate_of_rise} m/hr) indicates intense upstream mountain surge.")

        if current_soil_moisture >= config.threshold_soil_critical_pct:
            explanations.append(f"Soil moisture saturation is critically high ({current_soil_moisture}%), drastically reducing infiltration capacity.")
        elif current_soil_moisture >= 65.0:
            explanations.append(f"High slope moisture ({current_soil_moisture}%) indicates pre-saturated mountain soil.")

        if slope_deg >= config.threshold_slope_steep_deg:
            explanations.append(f"Steep topographical gradient ({slope_deg}°) sharply reduces time-to-peak hydrograph response.")

        if events_count > 0:
            explanations.append(f"Catchment has historical vulnerability with {events_count} past recorded flash flood disasters.")

        if not explanations:
            explanations.append("All hydrological parameters, river stages, and soil moisture levels remain within nominal seasonal baseline thresholds.")

        # 5. Recommendation Action
        recommendation = "Maintain regular hydrological monitoring."
        if risk_level == "CRITICAL":
            recommendation = "IMMEDIATE EVACUATION ADVISED: Trigger siren alarms, alert district emergency teams, and clear riverbank settlements."
        elif risk_level == "HIGH":
            recommendation = "HIGH READINESS: Mobilize quick-response personnel, activate emergency shelters, and advise vulnerable low-lying residents."
        elif risk_level == "MODERATE":
            recommendation = "ELEVATED VIGILANCE: Continuous radar tracking and sensor polling; notify local disaster relief coordinators."

        # 6. Historical Comparison
        hist_comp = {
            "past_events_count": events_count,
            "worst_event_name": worst_event.name if worst_event else "2013 Kedarnath Flash Flood",
            "worst_event_max_water_m": worst_event.maximum_water_level if worst_event else 12.4,
            "worst_event_rainfall_mm": worst_event.maximum_rainfall if worst_event else 325.0,
            "similarity_index_pct": round(min(100.0, (final_score / 100.0) * 88.0 + (12.0 if events_count > 0 else 0.0)), 1)
        }

        # Structure full response payload
        return {
            "watershed_id": watershed.id,
            "watershed_name": watershed.name,
            "watershed_code": watershed.code,
            "district": watershed.district,
            "state": watershed.state,
            "area_sq_km": watershed.area_sq_km,
            "risk_score": final_score,
            "risk_level": risk_level,
            "factors": {
                "rainfall": {
                    "score": round(rain_score, 1),
                    "weight": config.weight_rainfall,
                    "value": current_rainfall,
                    "unit": "mm/hr",
                    "description": "Instantaneous rainfall intensity"
                },
                "accumulated_rain": {
                    "score": round(acc_rain_score, 1),
                    "weight": config.weight_accumulated_rain,
                    "value": accumulated_rain_3h,
                    "unit": "mm (3h)",
                    "description": "3-Hour cumulative precipitation"
                },
                "river_level": {
                    "score": round(river_score, 1),
                    "weight": config.weight_river_level,
                    "value": current_river_level,
                    "unit": "m",
                    "description": "Current river stage depth"
                },
                "rate_of_rise": {
                    "score": round(rise_score, 1),
                    "weight": config.weight_rate_of_rise,
                    "value": rate_of_rise,
                    "unit": "m/hr",
                    "description": "Hydrograph water level rise velocity"
                },
                "soil_moisture": {
                    "score": round(soil_score, 1),
                    "weight": config.weight_soil_moisture,
                    "value": current_soil_moisture,
                    "unit": "%",
                    "description": "Catchment soil saturation"
                },
                "slope": {
                    "score": round(slope_score, 1),
                    "weight": config.weight_slope,
                    "value": slope_deg,
                    "unit": "degrees",
                    "description": "Topographical mountain gradient"
                },
                "historical_risk": {
                    "score": round(hist_score, 1),
                    "weight": config.weight_historical,
                    "value": events_count,
                    "unit": "events",
                    "description": "Recorded past flood disasters"
                }
            },
            "explanation": explanations,
            "historical_comparison": hist_comp,
            "recommendation": recommendation,
            "evaluated_at": now.isoformat()
        }


risk_engine = ExplainableFloodRiskEngine()
