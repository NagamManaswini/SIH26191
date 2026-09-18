import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.watershed import Watershed
from app.models.sensor import Sensor
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.historical import HistoricalFloodEvent
from app.models.prediction import FloodPrediction
from app.models.enums import RiskLevel


class BaselineTemporalForecaster:
    """
    Multi-horizon temporal flood forecasting engine (30, 60, 90, 120 min lead time).
    Prepares features for future Temporal Fusion Transformer (TFT) integrations.
    """

    HORIZONS = [30, 60, 90, 120]  # Minutes ahead
    FEATURE_NAMES = [
        "rainfall_5min",
        "rainfall_15min",
        "rainfall_30min",
        "rainfall_60min",
        "accumulated_rainfall",
        "river_level",
        "river_rate_of_rise",
        "soil_moisture",
        "elevation",
        "slope",
        "historical_risk",
    ]

    def __init__(self, model_version: str = "baseline-v1-temporal"):
        self.model_version = model_version
        self.training_date = "2026-09-15"
        self.danger_stage_m = 4.5
        self.critical_stage_m = 5.2

    def extract_features(
        self,
        rainfall_records: List[Dict[str, Any]],
        river_records: List[Dict[str, Any]],
        soil_records: List[Dict[str, Any]],
        watershed_meta: Dict[str, Any],
        historical_events_count: int = 0
    ) -> Dict[str, float]:
        """Extract 11 hydrological features from telemetry series."""
        r_rates = [r.get("rainfall_mm", 0.0) for r in rainfall_records] if rainfall_records else [0.0]
        
        rainfall_5min = float(r_rates[0]) if len(r_rates) > 0 else 0.0
        rainfall_15min = float(sum(r_rates[:3]) / max(1, len(r_rates[:3]))) if r_rates else rainfall_5min
        rainfall_30min = float(sum(r_rates[:6]) / max(1, len(r_rates[:6]))) if r_rates else rainfall_15min
        rainfall_60min = float(sum(r_rates[:12]) / max(1, len(r_rates[:12]))) if r_rates else rainfall_30min
        accumulated_rainfall = float(sum(r_rates[:15]) * 0.5) if r_rates else 0.0

        h_levels = [r.get("water_level_m", 1.85) for r in river_records] if river_records else [1.85]
        river_level = float(h_levels[0]) if len(h_levels) > 0 else 1.85
        
        if len(h_levels) >= 2:
            dh = h_levels[0] - h_levels[-1]
            dt_hours = max(0.2, len(h_levels) * 0.1)
            river_rate_of_rise = float(round(max(-2.0, min(5.0, dh / dt_hours)), 3))
        else:
            river_rate_of_rise = 0.0

        s_moistures = [r.get("moisture_percentage", 60.0) for r in soil_records] if soil_records else [60.0]
        soil_moisture = float(s_moistures[0]) if len(s_moistures) > 0 else 60.0

        elevation = float(watershed_meta.get("elevation_m", 1850.0))
        slope = float(watershed_meta.get("average_slope_deg", 24.5))
        historical_risk = float(min(100.0, historical_events_count * 35.0))

        return {
            "rainfall_5min": round(rainfall_5min, 2),
            "rainfall_15min": round(rainfall_15min, 2),
            "rainfall_30min": round(rainfall_30min, 2),
            "rainfall_60min": round(rainfall_60min, 2),
            "accumulated_rainfall": round(accumulated_rainfall, 2),
            "river_level": round(river_level, 2),
            "river_rate_of_rise": round(river_rate_of_rise, 3),
            "soil_moisture": round(soil_moisture, 1),
            "elevation": round(elevation, 1),
            "slope": round(slope, 1),
            "historical_risk": round(historical_risk, 1),
        }

    def _calculate_horizon_surge(self, horizon_min: int, f: Dict[str, float]) -> float:
        """Physical hydrological lag surge at lead-time t + horizon_min."""
        rain_recent = f.get("rainfall_15min", 0.0) * 0.4 + f.get("rainfall_5min", 0.0) * 0.6
        rain_accum = f.get("accumulated_rainfall", 0.0)
        curr_river = f.get("river_level", 1.85)
        rate_of_rise = f.get("river_rate_of_rise", 0.0)
        soil_sat = f.get("soil_moisture", 60.0) / 100.0
        slope = f.get("slope", 24.5)

        c_runoff = min(0.92, 0.35 + soil_sat * 0.45 + (slope / 45.0) * 0.15)
        t_factor = horizon_min / 60.0  # in hours

        time_to_peak_h = max(0.4, 1.6 - (slope / 50.0) * 0.6 - soil_sat * 0.4)
        hydro_wave = math.exp(-((t_factor - time_to_peak_h) ** 2) / (2 * (0.85 ** 2)))

        rainfall_surge = (rain_recent * c_runoff / 32.0) * hydro_wave * (1.0 + (rain_accum / 80.0))
        momentum_surge = max(0.0, rate_of_rise * t_factor * math.exp(-0.7 * t_factor))

        total_predicted = curr_river + rainfall_surge + momentum_surge
        return max(1.2, total_predicted)

    def _determine_risk_tier(self, water_level: float, flood_prob: float) -> str:
        if water_level >= self.critical_stage_m or flood_prob >= 80.0:
            return "CRITICAL"
        elif water_level >= self.danger_stage_m or flood_prob >= 55.0:
            return "HIGH"
        elif water_level >= 3.2 or flood_prob >= 25.0:
            return "MODERATE"
        else:
            return "LOW"

    def predict_multi_horizon(self, feature_dict: Dict[str, float]) -> List[Dict[str, Any]]:
        """Predict for +30, +60, +90, +120 minutes."""
        predictions = []
        rain_rate = feature_dict.get("rainfall_5min", 0.0)

        for minutes in self.HORIZONS:
            pred_level = round(self._calculate_horizon_surge(minutes, feature_dict), 2)

            # Uncertainty envelope
            uncertainty_std = 0.08 + (minutes / 120.0) * 0.28
            if rain_rate > 35.0:
                uncertainty_std *= 1.35

            conf_lower = max(1.0, round(pred_level - 1.645 * uncertainty_std, 2))
            conf_upper = round(pred_level + 1.645 * uncertainty_std, 2)

            z_score = (pred_level - self.danger_stage_m) / max(0.1, uncertainty_std * 1.5)
            flood_prob = 1.0 / (1.0 + math.exp(-1.4 * z_score))
            flood_prob_pct = round(min(99.0, max(2.0, flood_prob * 100.0)), 1)

            risk_level = self._determine_risk_tier(pred_level, flood_prob_pct)
            confidence_pct = round(max(60.0, 95.0 - (minutes / 120.0) * 16.0 - (0.05 * rain_rate)), 1)

            predictions.append({
                "minutes_ahead": minutes,
                "predicted_water_level": pred_level,
                "flood_probability": flood_prob_pct,
                "risk_level": risk_level,
                "confidence": confidence_pct,
                "confidence_lower": conf_lower,
                "confidence_upper": conf_upper
            })

        return predictions

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "model_version": self.model_version,
            "model_type": "Multi-Horizon Hydrological Lag Regressor (TFT-Ready Architecture)",
            "training_date": self.training_date,
            "prediction_horizons_min": self.HORIZONS,
            "features_used": self.FEATURE_NAMES,
            "target": "future_river_water_level_meters",
            "mean_confidence": 86.4,
            "disclaimer": "SIMULATED / DEMO PREDICTIONS: Not certified for direct operational civil evacuation without local authority verification."
        }

    def run_forecast_for_watershed(
        self,
        db: Session,
        watershed_id: int,
        persist: bool = False
    ) -> Dict[str, Any]:
        """Runs full inference for a given watershed from active database telemetry."""
        watershed = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not watershed:
            raise ValueError(f"Watershed with ID {watershed_id} not found.")

        sensor_ids = [s.id for s in watershed.sensors] if watershed.sensors else []
        now = datetime.now(timezone.utc)

        rain_records: List[Dict[str, Any]] = []
        river_records: List[Dict[str, Any]] = []
        soil_records: List[Dict[str, Any]] = []

        if sensor_ids:
            rr = db.query(RainfallReading).filter(
                RainfallReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(RainfallReading.timestamp)).limit(20).all()
            rain_records = [{"rainfall_mm": r.rainfall_mm, "timestamp": r.timestamp} for r in rr]

            rv = db.query(RiverReading).filter(
                RiverReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(RiverReading.timestamp)).limit(10).all()
            river_records = [{"water_level_m": r.water_level_m, "timestamp": r.timestamp} for r in rv]

            sm = db.query(SoilMoistureReading).filter(
                SoilMoistureReading.sensor_id.in_(sensor_ids)
            ).order_by(desc(SoilMoistureReading.timestamp)).limit(10).all()
            soil_records = [{"moisture_percentage": r.moisture_percentage, "timestamp": r.timestamp} for r in sm]

        hist_count = db.query(HistoricalFloodEvent).filter(
            HistoricalFloodEvent.location.ilike(f"%{watershed.name.split()[0]}%") |
            HistoricalFloodEvent.affected_area.ilike(f"%{watershed.district}%")
        ).count()

        watershed_meta = {
            "elevation_m": getattr(watershed, "elevation_m", 1850.0),
            "average_slope_deg": getattr(watershed, "average_slope_deg", 24.5),
            "area_sq_km": watershed.area_sq_km,
        }

        features = self.extract_features(
            rainfall_records=rain_records,
            river_records=river_records,
            soil_records=soil_records,
            watershed_meta=watershed_meta,
            historical_events_count=hist_count
        )

        horizon_predictions = self.predict_multi_horizon(features)

        if persist:
            for h in horizon_predictions:
                enum_risk = RiskLevel[h["risk_level"]] if hasattr(RiskLevel, h["risk_level"]) else RiskLevel.LOW
                db.add(FloodPrediction(
                    watershed_id=watershed.id,
                    prediction_time=now,
                    forecast_for=now + timedelta(minutes=h["minutes_ahead"]),
                    predicted_water_level=h["predicted_water_level"],
                    probability=h["flood_probability"],
                    risk_level=enum_risk,
                    confidence=h["confidence"],
                    model_version=self.model_version
                ))
            db.commit()

        # Add forecast timestamp to each prediction item
        formatted_predictions = []
        for h in horizon_predictions:
            forecast_time = now + timedelta(minutes=h["minutes_ahead"])
            formatted_predictions.append({
                **h,
                "forecast_timestamp": forecast_time.isoformat()
            })

        return {
            "watershed_id": watershed.id,
            "watershed_name": watershed.name,
            "watershed_code": watershed.code,
            "district": watershed.district,
            "state": watershed.state,
            "current_water_level": features["river_level"],
            "current_rainfall_rate": features["rainfall_5min"],
            "current_soil_moisture": features["soil_moisture"],
            "features_extracted": features,
            "predictions": formatted_predictions,
            "model_metadata": self.get_metadata(),
            "model_version": self.model_version,
            "generated_at": now.isoformat()
        }


ai_forecaster = BaselineTemporalForecaster()
