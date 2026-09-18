from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter(prefix="/overview", tags=["Overview"])

@router.get("/metrics")
async def get_overview_metrics() -> Dict[str, Any]:
    """
    Overview summary metrics for the landing dashboard cards.
    """
    return {
        "live_sensors": {
            "total_active": 48,
            "rainfall_gauges": 24,
            "water_level_radars": 16,
            "soil_moisture_probes": 8,
            "health_percentage": 98.2,
            "status": "Operational"
        },
        "flood_risk": {
            "current_risk_level": "MODERATE",
            "highest_risk_zone": "Catchment Sector 4 (Upper Valley)",
            "soil_saturation_avg": 74.5,
            "critical_micro_watersheds": 2
        },
        "ai_forecast": {
            "lead_time_minutes": 60,
            "model_confidence": 91.4,
            "forecast_peak_intensity_mm_hr": 42.0,
            "probability_of_inundation": 38.5,
            "trend": "Increasing"
        },
        "active_alerts": {
            "critical_count": 0,
            "warning_count": 2,
            "advisory_count": 5,
            "latest_alert": "Advisory: Elevated runoff expected in North Basin within 45 mins"
        }
    }
